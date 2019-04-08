"""

All functions which serve as a necessary component to a service

"""
import datetime
import json
import requests

import falcon

from sa.constants import SLACK_WEBHOOK_URL


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


def slack_notification(text, slack_webhook_url=SLACK_WEBHOOK_URL):
    return requests.post(
        slack_webhook_url,
        data=json.dumps({"text": text}),
        headers={"Content-Type": "application/json"},
    )
