"""
build.py
~~~~~~~~

This build script will remove any unnecessary files like unit tests or package
dist-info, pre-compile all project code into Python bytecode, remove all source files,
zip into an archive, deploy the archive onto AWS Lambda, and ensure the Lambda's
environment is up-to-date with `env_vars.json`.

Using compiled bytecode, rather than source files, will lead to faster execution.

"""
import configparser
import json
import os
import sys
import time

import boto3


AWS_PROFILE_NAME = "smartadvising"
AWS_REGION_NAME = "us-east-1"
FUNCTION_NAME = "smartadvising-api"

PYTHON_PROJECT_DIR = "sa"
PYTHON_PROJECT_PKG_DIR = "libs"
PYTHON_PATH = sys.executable

CONFIG_PARSER = configparser.ConfigParser()
CONFIG_PARSER.read("./config.ini")
DEFAULTS = {"environment": json.load(open("env_vars.json"))}
PYTHON_VERSION = "cpython-37"


boto3.setup_default_session(profile_name=AWS_PROFILE_NAME)
client = boto3.client("lambda", region_name=AWS_REGION_NAME)

if sys.argv[1] == "build":
    ts = int(time.time())
    zip_name = f"{FUNCTION_NAME}.zip"
    project_dir = os.path.dirname(os.path.realpath(__file__))
    dir_code = f"/tmp/project-{ts}-code"
    dir_libs = f"/tmp/project-{ts}-libs"

    # Ensure inside project directory
    os.chdir(project_dir)

    # Delete any existing zip archive, start fresh
    os.system(f"rm {zip_name}")

    # Clean-up any Python bytecode in existing libs or code
    os.system(f"find {project_dir} -name '*.pyc' -delete")
    os.system(
        f"find {project_dir} -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf"
    )

    # Make fresh copies of code and libs
    os.system(f"rm -rf {dir_code}")
    os.system(f"rm -rf {dir_libs}")
    os.system(f"cp -r {PYTHON_PROJECT_DIR} {dir_code}")
    os.system(f"cp -r {PYTHON_PROJECT_PKG_DIR} {dir_libs}")

    # Remove any unnecessary files like unit tests or package's dist-info
    os.system(
        f'find {dir_libs} -type d \( -iname "tests" -o -iname "testing" \) -exec rm -rdf {{}} +'
    )
    os.system(f'find {dir_libs} -name "*-info" -type d -exec rm -rdf {{}} +')

    for directory in [dir_code, dir_libs]:
        # Pre-compile all Python files into Python bytecode
        os.system(f"{PYTHON_PATH} -OO -m compileall {directory}")

        # Remove all .py files and move them from the __pycache__ directories to their top-level parent.
        os.system(
            f"find {directory} -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.{PYTHON_VERSION}//'); cp $f $n; done;"
        )
        os.system(
            f"find {directory} -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf"
        )
        os.system(f"find {directory} -type f -a -name '*.py' -print0 | xargs -0 rm -f")

    # Prepare to zip everything together
    os.chdir(f"{dir_libs}")

    # Move project code with the dependencies
    os.system(f"mv {dir_code} {PYTHON_PROJECT_DIR}")

    # Rename all optimized Python bytecode files to *.pyc
    os.system(
        r"""find . -type f -name "*.opt-2.pyc" | while read NAME; do mv "${NAME}" $(echo $NAME | sed 's/\(.*\).opt-2.pyc/\1.pyc/g'); done"""
    )

    # Zip the project code together
    os.system(f"zip -r {project_dir}/{zip_name} *")

    # Upload the archive and update environment on AWS Lambda
    os.chdir(project_dir)

    client.update_function_code(
        FunctionName=FUNCTION_NAME, ZipFile=open(f"{zip_name}", "rb").read()
    )

elif sys.argv[1] == "env":
    client.update_function_configuration(
        FunctionName=FUNCTION_NAME, Environment=DEFAULTS["environment"]
    )
