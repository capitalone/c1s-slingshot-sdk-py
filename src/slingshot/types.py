# ruff: noqa: UP045
"""Types used throughout this SDK."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Generic, Optional, TypeVar, Union

from typing_extensions import NotRequired, TypedDict

UNSET = ...
JSON_TYPE = Union[
    dict[str, "JSON_TYPE"],
    list["JSON_TYPE"],
    str,
    int,
    float,
    bool,
    None,
]


class AssignSettingsSchema(TypedDict):
    """Schema for assigning additional project settings in Slingshot."""

    sla_minutes: NotRequired[Optional[int]]
    fix_scaling_type: NotRequired[Optional[bool]]
    auto_apply_recs: NotRequired[Optional[bool]]
    optimize_instance_size: NotRequired[Optional[bool]]


class ProjectSchema(TypedDict):
    """Schema for a project in Slingshot."""

    created_at: Optional[str]
    updated_at: Optional[str]
    id: Optional[str]
    name: Optional[str]
    app_id: Optional[str]
    cluster_path: Optional[str]
    job_id: Optional[str]
    workspace_id: Optional[str]
    creator_id: Optional[str]
    product_code: Optional[str]
    description: Optional[str]
    settings: Optional[ProjectSettingsSchema]
    metrics: Optional[ProjectMetricsSchema]
    creator: Optional[ProjectCreatorSchema]
    phase: Optional[str]
    product_name: Optional[str]


class ProjectSettingsSchema(TypedDict):
    """Schema for retrieving the project additional settings in Slingshot."""

    sla_minutes: Optional[int]
    fix_scaling_type: Optional[bool]
    auto_apply_recs: Optional[bool]
    optimize_instance_size: Optional[bool]


class ProjectMetricsSchema(TypedDict):
    """Schema for retrieving the project metrics in Slingshot."""

    job_success_rate_percent: Optional[int]
    sla_met_percent: Optional[int]
    estimated_savings: Optional[int]


class ProjectCreatorSchema(TypedDict):
    """Schema for retrieving the project creator in Slingshot."""

    userId: Optional[str]
    auth0Id: Optional[str]
    tenantId: Optional[str]
    isTenantAdmin: Optional[bool]
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    isActive: Optional[bool]
    isRegistered: Optional[bool]


class RecommendationDetailsSchema(TypedDict):
    """Schema for retrieving the details of recommendation to a project in Slingshot."""

    created_at: Optional[str]
    updated_at: Optional[str]
    id: Optional[str]
    state: Optional[str]
    error: Optional[str]
    recommendation: Optional[RecommendationSchema]


class RecommendationSchema(TypedDict):
    """Schema for the recommendation of a project in Slingshot."""

    metrics: Optional[MetricsSchema]
    configuration: Optional[ConfigurationSchema]
    settings: Optional[SettingsSchema]


class MetricsSchema(TypedDict):
    """Schema for the recommended metrics in Slingshot."""

    spark_duration_minutes: Optional[int]
    spark_cost_requested_usd: Optional[int]


class ConfigurationSchema(TypedDict):
    """Schema for the recommended configuration in Slingshot."""

    enable_elastic_disk: Optional[bool]
    node_type_id: Optional[str]
    num_workers: Optional[int]
    autoscale: Optional[AutoscaleSchema]
    aws_attributes: Optional[AwsAttributesSchema]
    azure_attributes: Optional[AzureAttributesSchema]
    cluster_log_conf: Optional[ClusterLogConfSchema]
    default_tags: Optional[dict[str, str]]
    driver_node_type_id: Optional[str]
    spec: Optional[SpecSchema]


class AutoscaleSchema(TypedDict):
    """Schema for the autoscale configuration in a recommendation."""

    max_workers: Optional[int]
    min_workers: Optional[int]


class AwsAttributesSchema(TypedDict):
    """Schema for the AWS attributes in a recommendation."""

    availability: Optional[str]
    ebs_volume_count: Optional[int]
    ebs_volume_iops: Optional[int]
    ebs_volume_size: Optional[int]
    ebs_volume_throughput: Optional[int]
    ebs_volume_type: Optional[str]
    first_on_demand: Optional[int]
    spot_bid_price_percent: Optional[int]


class AzureAttributesSchema(TypedDict):
    """Schema for the Azure attributes in a recommendation."""

    availability: Optional[str]
    first_on_demand: Optional[int]
    spot_bid_max_price: Optional[int]


class ClusterLogConfSchema(TypedDict):
    """Schema for the cluster log configuration in a recommendation."""

    dbfs: Optional[DbfsLogConfSchema]
    s3: Optional[S3LogConfSchema]
    volumes: Optional[VolumesLogConfSchema]


class DbfsLogConfSchema(TypedDict):
    """Schema for DBFS log configuration in a cluster log configuration."""

    destination: Optional[str]


class S3LogConfSchema(TypedDict):
    """Schema for S3 log configuration in a cluster log configuration."""

    destination: Optional[str]
    canned_acl: Optional[str]
    enable_encryption: Optional[bool]
    encryption_type: Optional[str]
    endpoint: Optional[str]
    kms_key: Optional[str]
    region: Optional[str]


class VolumesLogConfSchema(TypedDict):
    """Schema for volume log configuration in a cluster log configuration."""

    destination: Optional[str]


class SpecSchema(TypedDict):
    """Schema for the spec in a recommendation."""

    enable_elastic_disk: Optional[bool]
    node_type_id: Optional[str]
    num_workers: Optional[int]
    driver_node_type_id: Optional[str]


class SettingsSchema(TypedDict):
    """Schema for additional project settings in Slingshot."""

    sla_minutes: Optional[int]
    fix_scaling_type: Optional[bool]
    auto_apply_recs: Optional[bool]
    optimize_instance_size: Optional[bool]


QueryParams = Mapping[str, Union[str, list[str]]]


T = TypeVar("T")


class Page(TypedDict, Generic[T]):
    """A page of items from a paginated collection."""

    page: int
    pages: int
    items: list[T]
