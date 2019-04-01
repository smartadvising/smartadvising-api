import json
import hashlib
import decimal
import dateutil
import datetime
import statistics
from distutils.util import strtobool

import falcon
import sqlalchemy
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from sa.models import *
from sa.utils import (
    get_required_arg,
    parse_date,
    print_log,
    random_with_N_digits,
    required_arguments,
    send_email,
    send_push_notification,
    slack_notification,
)


class UserResource(object):
    @staticmethod
    def hash_password(plaintext, salt):
        return hashlib.sha256("".join((plaintext, salt)).encode("utf-8")).hexdigest()

    @staticmethod
    def email_exists(db, email):
        """ Ensure incoming email is unique and unused """
        try:
            db.query(User).filter(User.email == email).one()
            return True
        except sqlalchemy.orm.exc.NoResultFound:
            return False
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise falcon.HTTPInternalServerError(
                description="Duplicate e-mails already exist"
            )

    def on_get(self, req, resp, user_id: int = None):
        users = []
        query = self.db.query(User)

        if user_id:
            users.append(query.filter(User.id == user_id).one())
        else:
            if "email" in req.data:
                query = query.filter(User.email == req.data["email"])

            users.extend(query.all())

        resp.body = {"users": [user.as_dict("password", "salt") for user in users]}

    @falcon.before(required_arguments, ("email", "password", "utility_id", "state_id"))
    def on_post(self, req, resp):
        email = req.data["email"]
        salt = str(req.timestamp)
        password = UserResource.hash_password(req.data["password"], salt)

        if UserResource.email_exists(self.db, email):
            raise falcon.HTTPConflict(description="Duplicate e-mails")

        user = User(email=email, password=password, salt=salt)

        if "phone_id" in req.data:
            try:
                user.phone_id = req.data["phone_id"]
                user.phone_os = PhoneOS.query.filter(
                    PhoneOS.name == req.data["phone_os"]
                ).one()
            except KeyError:
                raise falcon.HTTPBadRequest("Phone ID supplied but not Phone OS")

        if "utility_account_details" in req.data:
            user.utility_account_details = json.loads(
                req.data["utility_account_details"]
            )

        if "name" in req.data:
            user.name = req.data["name"]

        if "city" in req.data:
            user.city = req.data["city"]

        if "address" in req.data:
            user.address = req.data["address"]

        if "stripe_subscription_id" in req.data:
            user.stripe_subscription_id = req.data["stripe_subscription_id"]

        if "notif_freq" in req.data:
            user.notif_freq = req.data["notif_freq"]

        if "notif_days" in req.data:
            user.notif_days = req.data["notif_days"]

        if "notif_email" in req.data:
            user.notif_email = strtobool(req.data["notif_email"])

        if "average_usage" in req.data:
            user.average_usage = req.data["average_usage"]

        if "utility_id" in req.data:
            user.utility = (
                self.db.query(Utility)
                .filter(Utility.id == req.data["utility_id"])
                .one()
            )

        if "state_id" in req.data:
            user.state = (
                self.db.query(State).filter(State.id == req.data["state_id"]).one()
            )

        customer = stripe.Customer.create(
            description=f"sa customer for {user.email}", email=user.email
        )
        user.stripe_customer_id = customer.id

        self.db.User.save(user)
        self.db.commit()

        send_email(
            self.db,
            user.id,
            NOTIFICATION_TYPE_IDS["signup"],
            data={"format_subject": {}, "format_body": {}},
        )
        send_push_notification(
            self.db, user.id, NOTIFICATION_TYPE_IDS["signup"], data={"format_body": {}}
        )

        resp.status = falcon.HTTP_201
        resp.body = {"id": user.id, "stripe_id": user.stripe_customer_id}

    def on_patch(self, req, resp, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).one()

        if "email" in req.data:
            user.email = req.data["email"]

            try:
                self.db.User.save(user)
                self.db.commit()
            except sqlalchemy.exc.IntegrityError:
                raise falcon.HTTPConflict(description="Duplicate e-mails")

        if not req.data.get("alt_email"):
            req.data["alt_email"] = None

        for arg in [a for a in ["email", "alt_email"] if a in req.data]:
            setattr(user, arg, req.data[arg])

            self.db.User.save(user)
            try:
                self.db.commit()
            except OperationalError as e:
                print_log(e)
                raise falcon.HTTPBadRequest(
                    "Internal configuration error", status_code=500
                )
            except IntegrityError as e:
                print_log(e)
                raise falcon.HTTPBadRequest("Provided primary e-mail already exists")

        if "name" in req.data:
            user.name = req.data["name"]

        if "city" in req.data:
            user.city = req.data["city"]

        if "zipcode" in req.data:
            zipcode = req.data["zipcode"]

            try:
                if zipcodes.is_valid(zipcode):
                    if [
                        z for z in zipcodes.matching(zipcode) if z["city"] == user.city
                    ]:
                        raise falcon.HTTPBadRequest(
                            f"Invalid zipcode provided: {zipcode}"
                        )

                    user.zipcode = zipcode
            except (ValueError, TypeError) as e:
                raise falcon.HTTPBadRequest(str(e))

        if "phone_os_id" in req.data:
            user.phone_os_id = req.data["phone_os_id"]

        if "phone_id" in req.data:
            user.phone_id = req.data["phone_id"]

        if "address" in req.data:
            user.address = req.data["address"]

        if "stripe_subscription_id" in req.data:
            user.stripe_subscription_id = req.data["stripe_subscription_id"]

        if "notif_freq" in req.data:
            user.notif_freq = req.data["notif_freq"]

        if "notif_days" in req.data:
            user.notif_days = req.data["notif_days"]

        if "notif_email" in req.data:
            user.notif_email = strtobool(req.data["notif_email"])

        if "utility_account_details" in req.data:
            user.utility_account_details = json.loads(
                req.data["utility_account_details"]
            )

        if "password" in req.data:
            user.salt = str(req.timestamp)
            user.password = UserResource.hash_password(req.data["password"], user.salt)
            user.has_forgotten_password = False

        if "minimum_renewable" in req.data:
            user.minimum_renewable = req.data["minimum_renewable"]

        if "state_id" in req.data and "utility_id" in req.data:
            if user.state is None or str(user.state.id) != req.data["state_id"]:
                user.state = (
                    self.db.query(State).filter(State.id == req.data["state_id"]).one()
                )

                user.utility = (
                    self.db.query(Utility)
                    .filter(Utility.id == req.data["utility_id"])
                    .one()
                )

                # Set all existing contracts as expired as new utility means new
                # suppliers and plans
                user.contract.is_expired = True
                self.db.Contract.add(user.contract)

        if "utility_id" in req.data:
            # Only modify if the utility id is different than current
            if user.utility is None or str(user.utility.id) != req.data["utility_id"]:
                user.utility = (
                    self.db.query(Utility)
                    .filter(Utility.id == req.data["utility_id"])
                    .one()
                )

                # Set all existing contracts as expired as new utility means new
                # suppliers and plans
                user.contract.is_expired = True
                self.db.Contract.add(user.contract)

        self.db.User.save(user)
        self.db.commit()

        resp.status = falcon.HTTP_202

    def on_delete(self, req, resp, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).one()

        # Ensure all of the user's subscriptions are set expired
        try:
            UserSubscriptionResource.unsubscribe_user(self.db, user_id)
        except NoResultFound:
            pass  # User is not subscribed

        # Ensure the contract created for the user (and therefore potentially a custom
        # plan specially created for the user) is removed
        if user.contract:
            ContractResource.fully_cascading_delete(self.db, user.contract.id)

        self.db.User.destroy(user)
        self.db.commit()


class AuthenticateResource(object):
    @falcon.before(required_arguments, ("email",))
    def on_post(self, req, resp):
        user = self.db.query(User).filter(User.email == req.data["email"]).one()

        if "password" in req.data:
            password = UserResource.hash_password(req.data["password"], user.salt)

            if user.password != password:
                raise falcon.HTTPBadRequest(
                    f'Invalid authentication details for user with id "{user.id}" were specified.'
                )

        elif "reset_pin" in req.data:
            if not user.has_forgotten_password:
                raise falcon.HTTPBadRequest(
                    f'User with id "{user.id}" has not forgotten their password, so reset pin cannot be used'
                )

            reset_pin = req.data["reset_pin"]

            if user.reset_pin != reset_pin:
                raise falcon.HTTPBadRequest(
                    f'Invalid reset pin for user with id "{user.id}" was specified'
                )

            user.has_forgotten_password = False
            self.db.User.save(user)
            self.db.commit()

        else:
            raise falcon.HTTPBadRequest(f"No authentication details specified")

        resp.body = {"user": {"id": user.id}}


class FactResource(object):
    def on_get(self, req, resp):
        resp.body = {"facts": [f.as_dict() for f in self.db.query(Fact).all()]}


class MajorResource(object):
    def on_get(self, req, resp, state_id: int = None):
        states = []
        query = self.db.query(State)

        if state_id:
            states.append(query.filter(State.id == state_id).one())
        else:
            states.extend(query.all())

        states = [state.as_dict() for state in states]

        resp.body = {"states": states}
