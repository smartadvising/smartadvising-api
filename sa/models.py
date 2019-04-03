"""
These models are used by SQLService to interact with a MySQL RDS database

"""
__all__ = [
    "Model",
    "Student",
    "Advisor",
    "College",
    "Major",
    "Faq",
]

import json
import decimal
import datetime

from sqlalchemy import Column, ForeignKey, Table, Enum, orm
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME, BOOLEAN, TEXT
import sqlservice


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def as_dict(self, *exclude):
    if not exclude:
        exclude = []

    exclude = [".".join([self.__tablename__, c]) for c in exclude]

    return {
        c.name: getattr(self, c.name)
        for c in self.__table__.columns
        if str(c) not in exclude
    }


Model = sqlservice.declarative_base()
Model.as_dict = as_dict


advisor_college = sqlalchemy.Table(
    "AdvisorCollege",
    Model.metadata,
    Column("advisor_id", INTEGER, ForeignKey("Advisor.id")),
    Column("college_id", INTEGER, ForeignKey("College.id")),
)


class Student(Model):
    __tablename__ = "Student"

    id = Column(INTEGER, primary_key=True)
    first_name = Column(VARCHAR(255))
    last_name = Column(VARCHAR(255))
    fsu_id = Column(VARCHAR(20))
    email = Column(VARCHAR(95), unique=True, nullable=False)

    is_undergraduate = Column(BOOLEAN, nullable=False, default=True)

    # many students to one major
    major_id = Column(INTEGER, ForeignKey("Major.id"))
    major = orm.relation("Major", uselist=False, back_populates="Student")


class Major(Model):
    __tablename__ = "Major"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255))

    # many majors to one college
    college_id = Column(INTEGER, ForeignKey("College.id"))
    college = orm.relation("College", uselist=False)

    # one major to many students
    students = orm.relation("Major", back_populates="major")


class College(Model):
    __tablename__ = "College"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255))

    # one college to many majors
    majors = orm.relation("Major", back_populates="college")


class Advisor(Model):
    __tablename__ = "Utility"

    id = Column(INTEGER, primary_key=True)
    first_name = Column(VARCHAR(255))
    last_name = Column(VARCHAR(255))

    title = Column(VARCHAR(255))
    phone_number = Column(VARCHAR(64))
    email = Column(VARCHAR(255))
    office_number = Column(VARCHAR(255))
    hours = Column(VARCHAR(255))
    description = Column(TEXT)

    colleges = orm.relation("College", secondary=advisor_college)


class Faq(Model):
    __tablename__ = "Fact"

    id = Column(INTEGER, primary_key=True)

    question = Column(TEXT, nullable=False)
    answer = Column(TEXT, nullable=False)
