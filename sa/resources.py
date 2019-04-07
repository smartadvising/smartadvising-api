__all__ = [
    "StudentResource",
    "AdvisorResource",
    "CollegeResource",
    "MajorResource",
    "QueueResource",
    "QueuerResource",
    "FaqResource",
]

from distutils.util import strtobool

import falcon
import sqlalchemy
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from sa.models import Student, Advisor, College, Major, Faq
from sa.utils import parse_date, required_arguments


class StudentResource:
    def on_get(self, req, resp, student_id: int = None):
        students = []
        query = self.db.query(Student)

        if student_id:
            students.append(query.filter(Student.id == student_id).one())
        else:
            if "email" in req.data:
                query = query.filter(Student.email == req.data["email"])

            students.extend(query.all())

        resp.body = {"students": [student.as_dict("password", "salt") for student in students]}

    @falcon.before(
        required_arguments, ("first_name", "last_name", "email", "password", "zipcode")
    )
    def on_post(self, req, resp):
        student = Student()

        student.first_name = req.data["first_name"]
        student.last_name = req.data["last_name"]
        student.email = req.data["email"]
        student.password = req.data["password"]
        student.zipcode = req.data["zipcode"]

        self.db.Student.save(student)
        self.db.commit()

        resp.status = falcon.HTTP_201
        resp.body = {"student_id": student.id}


class AdvisorResource:
    def on_get(self, req, resp, advisor_id: int = None):
        advisors = []
        query = self.db.query(Advisor)

        if advisor_id:
            advisors.append(query.filter(Advisor.id == advisor_id).one())
        else:
            if "owner_id" in req.data:
                query = query.filter(Advisor.owner.id == int(req.data["owner_id"]))

            advisors.extend(query.all())

        resp.body = {"advisors": [advisor for advisor in advisors]}

    @falcon.before(
        required_arguments,
        (
            "name",
            "owner_id",
            "college",
            "weight_lbs",
            "sex",
            "type",
            "date_birth",
            "bathroom_location",
            "activity_level",
        ),
    )
    def on_post(self, req, resp):
        advisor = Advisor(None)

        advisor.name = req.data["name"]
        advisor.owner_id = req.data["owner_id"]
        advisor.weight_lbs = int(req.data["weight_lbs"])
        advisor.sex = strtobool(req.data["sex"])
        advisor.type = req.data.get("type", advisor.type)
        advisor.date_birth = parse_date(req.data["date_birth"])
        advisor.bathroom_location = req.data.get(
            "bathroom_location", advisor.bathroom_location
        )
        advisor.activity_level = req.data.get("activity_level", advisor.activity_level)

        # many advisors to many traits
        for trait_value in req.data["traits"]:
            try:
                trait = self.db.query(Trait).filter(Trait.value == trait_value).one()
            except sqlalchemy.orm.exc.NoResultFound:
                trait = Trait(value=trait_value)
                self.db.Trait.save(trait)

            self.db.Trait.save(trait)
            advisor.traits.append(trait)

        # many advisors to many colleges
        for college_name in req.data["colleges"]:
            try:
                college = self.db.query(College).filter(College.name == college_name).one()
            except sqlalchemy.orm.exc.NoResultFound:
                college = College()
                college.name = college_name
                self.db.College.save(college)

            self.db.College.save(college)
            advisor.colleges.append(college)

        self.db.Advisor.save(advisor)
        self.db.commit()

        resp.status = falcon.HTTP_201
        resp.body = {"advisor_id": advisor.id}


class CollegeResource:
    def on_get(self, req, resp, college_id: int = None):
        colleges = []
        query = self.db.query(College)

        if college_id:
            colleges.append(query.filter(College.id == college_id).one())
        else:
            if "information" in req.data:
                query = query.filter(College.information == int(req.data["information"]))

            colleges.extend(query.all())

        resp.body = {"colleges": [college for college in colleges]}


class MajorResource:
    def on_get(self, req, resp, major_id: int = None):
        majores = []
        query = self.db.query(Major)

        if major_id:
            majores.append(query.filter(Major.id == major_id).one())
        else:
            if "owner_id" in req.data:
                query = query.filter(Major.owner.id == int(req.data["owner_id"]))

            majores.extend(query.all())

        resp.body = {
            "majores": [
                major.as_dict("password", "salt") for major in majores
            ]
        }


class FaqResource:
    def on_get(self, req, resp, faq_id: int = None):
        faqs = []
        query = self.db.query(Faq)

        if faq_id:
            faqs.append(query.filter(Faq.id == faq_id).one())
        else:
            if "owner_id" in req.data:
                query = query.filter(Faq.owner.id == int(req.data["owner_id"]))

            faqs.extend(query.all())

        resp.body = {
            "faqs": [faq.as_dict("password", "salt") for faq in faqs]
        }
