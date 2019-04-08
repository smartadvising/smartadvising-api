import json
import os

import sqlservice
import sqlalchemy


with open("env_vars.json") as f:
    env_vars = json.load(f)["Variables"]

for k, v in env_vars.items():
    os.environ[k] = v

import sa

db = sqlservice.SQLClient(
    {"SQL_DATABASE_URI": sa.constants.SQLALCHEMY_DATABASE_URI},
    model_class=sa.models.Model,
)

db.drop_all()
db.create_all()
db.commit()

c = sa.models.College(name="Florida State University", email_tld="my.fsu.edu")
db.College.save(c)

with open("advisors.json") as f:
    advisors_json = json.load(f)

for major, advisors in advisors_json.items():
    m = sa.models.Major(name=major, college_id=c.id)
    db.Major.save(m)
    db.commit()

    for advisor in advisors:
        for student_level in advisor["advises_for"]:
            a = sa.models.Advisor(
                name=advisor["name"],
                email=advisor["email"],
                is_undergraduate=student_level.lower() == "Undergraduate",
                major_id=m.id,
            )
            db.Advisor.save(a)

    db.Major.save(m)

db.commit()
# except sqlalchemy.orm.exdb.NoResultFound:
