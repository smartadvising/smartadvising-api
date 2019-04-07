import json
import os

import sqlservice
import sqlalchemy


with open('env_vars.json') as f:
    env_vars = json.load(f)["Variables"]

for k, v in env_vars.items():
    os.environ[k] = v

import sa

c = sqlservice.SQLClient(
    {"SQL_DATABASE_URI": sa.constants.SQLALCHEMY_DATABASE_URI},
    model_class=sa.models.Model,
)

c.drop_all()
c.create_all()
c.commit()

#except sqlalchemy.orm.exc.NoResultFound:
