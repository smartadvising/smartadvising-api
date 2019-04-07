"""
These models are used by SQLService to interact with a MySQL RDS database

"""
__all__ = ["Model", "Student", "Advisor", "College", "Major", "Faq", "Queuer"]

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


class Student(Model):
    __tablename__ = "Student"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255))
    student_identifier = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(95), unique=True, nullable=False)
    is_undergraduate = Column(BOOLEAN, nullable=False, default=True)
    # many students to one major
    major_id = Column(INTEGER, ForeignKey("Major.id"))
    major = orm.relation("Major", uselist=False, back_populates="students")


class Major(Model):
    __tablename__ = "Major"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255))

    # many majors to one college
    college_id = Column(INTEGER, ForeignKey("College.id"), nullable=False)
    college = orm.relation("College", uselist=False)

    # one to many students
    students = orm.relation("Student", back_populates="major")
    advisor = orm.relation("Advisor", back_populates="major")


class College(Model):
    __tablename__ = "College"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    email_tld = Column(VARCHAR(255), nullable=False, unique=True)

    # one college to many majors
    majors = orm.relation("Major", back_populates="college")


class Advisor(Model):
    __tablename__ = "Advisor"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    is_undergraduate = Column(BOOLEAN, nullable=False)

    major_id = Column(INTEGER, ForeignKey("Major.id"))
    major = orm.relation("Major", uselist=False, back_populates="advisor")


class Faq(Model):
    __tablename__ = "Faq"

    id = Column(INTEGER, primary_key=True)

    question = Column(TEXT, nullable=False)
    answer = Column(TEXT, nullable=False)


class Queuer(Model):
    __tablename__ = "Queuer"

    id = Column(INTEGER, primary_key=True)
    major_id = Column(INTEGER, ForeignKey("Major.id"))
    major = orm.relation("Major", uselist=False)
    is_undergraduate = Column(BOOLEAN, nullable=False, default=True)

    student_id = Column(INTEGER, ForeignKey("Student.id"))
    position = Column(INTEGER, nullable=False, default=1)
