"""
All functions which serve as a necessary component to a service

:author: Sean Pianka

"""
import datetime
import json
import requests

import falcon

from sa.constants import SLACK_WEBHOOK_URL


def required_arguments(req, resp, resource, params, required_args):
    """ Require specific arguments to be provided from caller a request is made.
    This ensures that the listed `required_args` are provided and accessible
    within the view.

    """
    if not all(arg in req.data for arg in required_args):
        not_provided = [arg for arg in required_args if arg not in req.data]
        raise falcon.HTTPMissingParam(not_provided[0])

    for arg in req.data:
        if arg in required_args:
            if not isinstance(arg, required_args[arg]):
                try:
                    required_args[arg](req.data[arg])
                except (ValueError, TypeError) as e:
                    slack_notification(f"{e}; {arg}, {required_args[arg]}")
                    raise falcon.HTTPInvalidParam(
                        f'`{arg}` ("{req.data[arg]}") type mismatch: provided type {type(arg)}, expected {required_args[arg]}',
                        arg,
                    )


def slack_notification(text, slack_webhook_url=SLACK_WEBHOOK_URL):
    return requests.post(
        slack_webhook_url,
        data=json.dumps({"text": text}),
        headers={"Content-Type": "application/json"},
    )
