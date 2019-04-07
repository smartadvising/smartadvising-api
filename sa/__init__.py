"""
Smart Advising
~~~~~~~~~~~~~~~

Below is an implementation of the Backend API

- Falcon and SQLService + SQLAlchemy
- Designed for Serverless

:author: Sean Pianka
:email: sean@lunabit.io
:org: Lunabit

"""
import traceback

import falcon
import sqlalchemy

from sa.constants import SQLALCHEMY_DATABASE_URI
from sa.middleware import (
    MetadataLoggingComponent,
    AppTokenComponent,
    JSONSerializeResponseComponent,
    DatabaseSessionComponent,
    lambda_adapter,
)


# Entry point
def handler(event, context):
    return lambda_adapter(api, event, context)


def generic_error_handler(ex, req, resp, params):
    from sa.utils import slack_notification

    error_log_text = (
        f'*[ERROR {resp.status} {req.method} {req.path}]*: "{traceback.format_exc()}"'
    )

    # Ensure NoResultFound errors are treated as a bad request
    if isinstance(ex, sqlalchemy.orm.exc.NoResultFound):
        ex = falcon.HTTPBadRequest(
            description=f"{str(ex)}: requested resource not found."
        )
        resp.status = falcon.HTTP_400

    # Transform all errors into an error Falcon expects
    if not isinstance(ex, falcon.HTTPError):
        ex = falcon.HTTPInternalServerError(description=str(ex))
        resp.status = falcon.HTTP_500

    slack_notification(error_log_text)

    raise ex


api = falcon.API(
    middleware=[
        MetadataLoggingComponent(),
        AppTokenComponent(),
        JSONSerializeResponseComponent(),
        DatabaseSessionComponent(SQLALCHEMY_DATABASE_URI),
    ]
)
api.add_error_handler(Exception, generic_error_handler)

from sa.resources import (
    StudentResource,
    AdvisorResource,
    CollegeResource,
    MajorResource,
    QueueResource,
    QueuerResource,
    FaqResource,
)


class_to_route_names_table = {}

for cls in (
    StudentResource,
    AdvisorResource,
    CollegeResource,
    MajorResource,
    QueueResource,
    QueuerResource,
    FaqResource,
):
    name = cls.__name__.rsplit("Resource", 1)[0].lower()

    try:
        plural_name = class_to_route_names_table[name]
    except KeyError:
        plural_name = "".join((name, "s"))

    api.add_route(f"/{plural_name}", cls())
    api.add_route(f"/{plural_name}/{{{name}_id}}", cls())
