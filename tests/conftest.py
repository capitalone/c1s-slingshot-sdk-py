import json


def get_aws_rec_from_file():
    with open("tests/test_files/aws_recommendation.json") as rec_in:
        return json.loads(rec_in.read())


def get_azure_rec_from_file():
    with open("tests/test_files/azure_recommendation.json") as rec_in:
        return json.loads(rec_in.read())


def get_project_from_file():
    with open("tests/test_files/project.json") as project_in:
        return json.loads(project_in.read())


def get_job_from_file():
    with open("tests/test_files/databricks_job.json") as job_in:
        return json.loads(job_in.read())
