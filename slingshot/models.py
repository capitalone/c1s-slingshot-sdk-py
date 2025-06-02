"""
Models used throughout this SDK
"""

from enum import Enum, unique
from typing import Dict, Generic, TypeVar, Union

from pydantic import BaseModel, root_validator, validator
from pydantic.generics import GenericModel


class Platform(str, Enum):
    AWS_DATABRICKS = "aws-databricks"
    AZURE_DATABRICKS = "azure-databricks"


class Error(BaseModel):
    code: str
    message: str

    def __str__(self):
        return f"{self.code}: {self.message}"


class ProjectError(Error):
    code: str = "Project Error"


class RecommendationError(Error):
    code: str = "Recommendation Error"


@unique
class DatabricksComputeType(str, Enum):
    ALL_PURPOSE_COMPUTE = "All-Purpose Compute"
    JOBS_COMPUTE = "Jobs Compute"
    JOBS_COMPUTE_LIGHT = "Jobs Compute Light"


class DatabricksError(Error):
    code: str = "Databricks Error"


class DatabricksAPIError(Error):
    @root_validator(pre=True)
    def validate_error(cls, values):
        values["code"] = "Databricks API Error"
        if values.get("error_code"):
            values["message"] = f"{values['error_code']}: {values.get('message')}"

        return values


DataType = TypeVar("DataType")


class Response(GenericModel, Generic[DataType]):
    result: Union[DataType, None] = None
    error: Union[Error, None] = None

    @validator("error", always=True)
    def check_consistency(cls, err, values):
        if err is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if err is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return err


class S3ClusterLogConfiguration(BaseModel):
    destination: str
    region: str
    enable_encryption: bool
    canned_acl: str


class DBFSClusterLogConfiguration(BaseModel):
    destination: str


class AWSProjectConfiguration(BaseModel):
    node_type_id: str
    driver_node_type: str
    custom_tags: Dict
    cluster_log_conf: Union[S3ClusterLogConfiguration, DBFSClusterLogConfiguration]
    cluster_name: str
    num_workers: int
    spark_version: str
    runtime_engine: str
    autoscale: Dict
    spark_conf: Dict
    aws_attributes: Dict
    spark_env_vars: Dict


class AzureProjectConfiguration(BaseModel):
    node_type_id: str
    driver_node_type: str
    cluster_log_conf: DBFSClusterLogConfiguration
    custom_tags: Dict
    num_workers: int
    spark_conf: Dict
    spark_version: str
    runtime_engine: str
    azure_attributes: Dict


IAMRoleRequiredPermissions = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SlingshotEC2Permissions",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes",
                "ec2:DescribeAvailabilityZones",
            ],
            "Resource": "*",
        }
    ],
}

IAMRoleTrustPolicy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                # SLI-19250 Make sure this is correct/allowed
                "AWS": "arn:aws:iam::533267411813:role/slingshot-data-collector"
            },
            "Action": "sts:AssumeRole",
            "Condition": {"StringEquals": {"sts:ExternalId": "PLACEHOLDER_EXTERNAL_ID"}},
        }
    ],
}
