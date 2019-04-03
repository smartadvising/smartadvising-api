"""
    Definitions for API middleware
"""
import json
import sys
from io import BytesIO
from urllib import parse

import falcon
import sqlservice

from sa.models import Model as BaseModel, Encoder
from sa.constants import SA_APP_TOKEN


def lambda_adapter(app, event, context):
    start_response = Response()
    output = app(environ(event, context), start_response)
    return start_response.build_lambda_response(output)


def environ(event, context):
    body = (event.get("body") or "").encode("utf-8")
    headers = {
        key.upper().replace("-", "_"): val
        for key, val in (event.get("headers") or {}).items()
    }

    remote_addr, *_ = headers.get("X_FORWARDED_FOR", "127.0.0.1").partition(", ")

    environ = {
        "SCRIPT_NAME": "",
        "REQUEST_METHOD": event["httpMethod"],
        "PATH_INFO": event["path"],
        "QUERY_STRING": parse.urlencode(event["queryStringParameters"] or {}, safe=","),
        "REMOTE_ADDR": remote_addr,
        "CONTENT_TYPE": headers.get("CONTENT_TYPE"),
        "CONTENT_LENGTH": str(len(body) or ""),
        "HTTP": "on",
        "SERVER_NAME": headers.get("HOST"),
        "SERVER_PORT": headers.get("X_FORWARDED_PORT"),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.input": BytesIO(body),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "wsgi.url_scheme": headers.get("X_FORWARDED_PROTO"),
        # Push all headers in
        **{f"HTTP_{name}": val for name, val in headers.items()},
    }

    return environ


class Response(object):
    def __init__(self):
        self.status = 500
        self.headers = []
        self.body = BytesIO()

    def __call__(self, status, headers, exc_info=None):
        self.status, *_ = status.split()
        self.headers = headers

        return self.body.write

    def build_lambda_response(self, wsgi_resp):
        body = "".join(
            map(lambda s: s.decode("utf-8"), [self.body.getvalue()] + list(wsgi_resp))
        )

        return {
            "statusCode": str(self.status),
            "headers": dict(self.headers),
            "body": body,
        }


class AppTokenComponent(object):
    def process_request(self, req, resp):
        from sa.utils import slack_notification

        """ Process the request before routing it. """
        if req.method in [
            "GET",
            "PATCH",
            "PUT",
            "DELETE",
            "HEAD",
            "OPTIONS",
        ]:  # HTTP/1.1
            req.data = req.params
        else:
            req.data = json.load(req.bounded_stream)

        try:
            if req.data["app_token"] != SA_APP_TOKEN:
                raise falcon.HTTPUnauthorized(
                    description="Invalid authentication token"
                )
        except KeyError:
            raise falcon.HTTPMissingParam("app_token")

        try:
            req.timestamp = int(float(req.data["timestamp"]))
        except KeyError:
            raise falcon.HTTPMissingParam(param_name="timestamp")
        except TypeError:
            raise falcon.HTTPInvalidParam(
                msg="Request timestamp must be provided", param_name="timestamp"
            )


class JSONSerializeResponseComponent(object):
    def process_response(self, req, resp, resource, req_succeeded):
        resp.body = json.dumps(resp.body, cls=Encoder)


class MetadataLoggingComponent(object):
    def process_request(self, req, resp):
        print(f"{req.method} {req.path}")


class DatabaseSessionComponent(object):
    """ Initiates a new Session for incoming request and closes it in the end. """

    def __init__(self, sqlalchemy_database_uri):
        self.sqlalchemy_database_uri = sqlalchemy_database_uri

    def process_resource(self, req, resp, resource, params):
        resource.db = sqlservice.SQLClient(
            {
                "SQL_DATABASE_URI": self.sqlalchemy_database_uri,
                "SQL_ISOLATION_LEVEL": "SERIALIZABLE",
                "SQL_ECHO": False,
                "SQL_ECHO_POOL": False,
                "SQL_CONVERT_UNICODE": True,
                "SQL_POOL_RECYCLE": 3600,
                "SQL_AUTOCOMMIT": False,
                "SQL_AUTOFLUSH": True,
                "SQL_EXPIRE_ON_COMMIT": True,
            },
            model_class=BaseModel,
        )
        # resource.db.drop_all()
        # resource.db.create_all()
        # resource.db.commit()

    def process_response(self, req, resp, resource):
        if hasattr(resource, "db"):
            resource.db.disconnect()
