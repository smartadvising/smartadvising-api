import datetime
import random
import json
import requests

import falcon
import boto3


def print_log(msg):
    """ Log important information to the terminal, including UTC time of an event. """
    now = datetime.datetime.now()
    time_format = (now.year, now.month, now.day, now.hour, now.minute, now.second)
    print("[{:02}-{:02}-{:02} {:02}:{:02}:{:02}]: {}".format(*time_format, msg))


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1

    return random.randint(range_start, range_end)


def parse_date(date_str: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(date_str, "%m/%d/%Y")
    except TypeError:
        raise falcon.HTTPBadRequest("Specified date is of an invalid type.")
    except ValueError:
        raise falcon.HTTPBadRequest("Specified date does not match format '%m/%d/%Y'.")


def floor_unix_epoch(epoch_time: float) -> int:
    """ Return floored epoch_time as an integer. """
    try:
        return int(float(epoch_time))
    except TypeError:
        raise falcon.HTTPBadRequest(
            "Timestamp is not a valid integer or floating-point number."
        )


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
