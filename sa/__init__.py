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

api.add_route("/advisors", AdvisorResource())
api.add_route("/advisors/{advisor_id}", AdvisorResource())
api.add_route("/colleges", CollegeResource())
api.add_route("/colleges/{college_id}", CollegeResource())
api.add_route("/colleges/{college_id}/majors", MajorResource())
api.add_route("/colleges/{college_id}/majors/{major_id}", MajorResource())
api.add_route("/faqs", FaqResource())
api.add_route("/faqs/{faq_id}", FaqResource())
api.add_route("/queuers", QueuerResource())
api.add_route("/queuers/{queuer_id}", QueuerResource())
api.add_route("/queues", QueueResource())
api.add_route("/students", StudentResource())
api.add_route("/students/{student_id}", StudentResource())
