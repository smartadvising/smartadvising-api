"""

All functions which serve as a necessary component to a service

"""
import datetime
import json
import requests

import falcon
import boto3

from sa.constants import SLACK_TOKEN, SLACK_CHANNEL
from sa.models import User


def parse_date(date_str: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(date_str, "%m/%d/%Y")
    except TypeError:
        raise falcon.HTTPBadRequest("Specified date is of an invalid type.")
    except ValueError:
        raise falcon.HTTPBadRequest("Specified date does not match format '%m/%d/%Y'.")


def required_arguments(req, resp, resource, params, required_args):
    """ Require specific arguments to be provided from caller a request is made.
    This ensures that the listed `required_args` are provided and accessible
    within the view.

    """
    if not all(arg in req.data for arg in required_args):
        not_provided = [arg for arg in required_args if arg not in req.data]

        raise falcon.HTTPMissingParam(not_provided[0])


def get_required_arg(data, key):
    try:
        return data[key]
    except KeyError:
        raise falcon.HTTPMissingParam(key)


def slack_notification(text, slack_channel=SLACK_CHANNEL):
    return requests.post(
        "https://slack.com/api/chat.postMessage",
        data=json.dumps(
            {
                "channel": slack_channel,
                "text": text,
                "as_user": False,
                "username": "sa",
            }
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(SLACK_TOKEN),
        },
    )


def send_email(db, recipient_id: int, notification_type_id: int, data: dict = None):
    client = boto3.client("sqs")
    user = db.query(User).filter(User.id == recipient_id).one()
    if not data:
        data = {}

    client.send_message(
        QueueUrl=client.get_queue_url(QueueName="sa-ses-outbox")["QueueUrl"],
        MessageBody=json.dumps(
            {
                "user_id": recipient_id,
                "notification_type_id": notification_type_id,
                "email": user.email,
                "format_body": data.get("format_body", []),
                "format_subject": data.get("format_subject", []),
            }
        ),
    )


def send_push_notification(
    db, recipient_id: int, notification_type_id: int, data: dict = None
):
    user = db.query(User).filter(User.id == recipient_id).one()

    if not data:
        data = {}

    # Only attempt to send a phone notification if the user has phone_id set
    if not user.phone_id:
        return

    client = boto3.client("sqs")
    client.send_message(
        QueueUrl=client.get_queue_url(QueueName="sa-mobile-push")["QueueUrl"],
        MessageBody=json.dumps(
            {
                "user_id": recipient_id,
                "notification_type_id": notification_type_id,
                "phone_id": user.phone_id,
                "format_body": data.get("format_body", []),
            }
        ),
    )
