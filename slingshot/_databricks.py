"""
Utilities for interacting with Databricks
"""

import logging
from collections import defaultdict
from typing import Collection, Dict, List, Optional, Tuple, Union

from slingshot.api import projects
from slingshot.clients.databricks import get_default_client
from slingshot.config import CONFIG  # noqa F401
from slingshot.models import (
    DatabricksAPIError,
    DatabricksError,
    Response,
)
from slingshot.utils.json import deep_update

logger = logging.getLogger(__name__)


def get_cluster(cluster_id: str) -> Response[dict]:
    """Get Databricks cluster.

    :param cluster_id: cluster ID
    :type cluster_id: str
    :return: cluster object
    :rtype: Response[dict]
    """
    cluster = get_default_client().get_cluster(cluster_id)
    if "error_code" in cluster:
        return Response(error=DatabricksAPIError(**cluster))

    return Response(result=cluster)


def create_and_apply_project_recommendation(project_id: str, job_id: str) -> Response[str]:
    """Create recommendation for project and apply it to the job

    :param job_id: ID of job to which the recommendation should be applied
    :type job_id: str
    :param project_id: ID of project for job
    :type project_id: str
    :return: ID of applied recommendation
    :rtype: Response[str]
    """
    recommendation_response = projects.create_project_recommendation(project_id)

    if recommendation_response.error:
        return recommendation_response

    recommendation_id = recommendation_response.result

    recommendation_wait_response = projects.wait_for_recommendation(project_id, recommendation_id)

    if recommendation_wait_response.error:
        return recommendation_wait_response

    return apply_project_recommendation(job_id, project_id, recommendation_id)


def apply_project_recommendation(
    job_id: str, project_id: str, recommendation_id: str
) -> Response[str]:
    """Updates jobs with project recommendation

    :param job_id: ID of job to apply prediction to
    :type job_id: str
    :param project_id: Slingshot project ID
    :type project_id: str
    :param recommendation_id: Slingshot project recommendation ID
    :type recommendation_id: str
    :return: ID of applied recommendation
    :rtype: Response[str]
    """
    databricks_client = get_default_client()

    job = databricks_client.get_job(job_id)
    job_clusters = _get_project_job_clusters(job)

    project_cluster = job_clusters.get(project_id)
    if not project_cluster:
        if len(job_clusters) == 1:
            project_cluster = next(iter(job_clusters.values()))
        else:
            return Response(
                error=DatabricksError(
                    message=f"Failed to locate cluster in job {job_id} for project {project_id}"
                )
            )

    project_cluster_path, project_cluster_def = project_cluster

    new_cluster_def_response = get_recommendation_cluster(
        project_cluster_def, project_id, recommendation_id
    )
    if new_cluster_def_response.error:
        return new_cluster_def_response
    new_cluster_def = new_cluster_def_response.result

    if project_cluster_path[0] == "job_clusters":
        new_settings = {
            "job_clusters": [
                {"job_cluster_key": project_cluster_path[1], "new_cluster": new_cluster_def}
            ]
        }
    else:
        new_settings = {
            "tasks": [{"task_key": project_cluster_path[1], "new_cluster": new_cluster_def}]
        }

    response = databricks_client.update_job(job_id, new_settings)

    if "error_code" in response:
        return Response(error=DatabricksAPIError(**response))

    return Response(result=recommendation_id)


def get_recommendation_job(job_id: str, project_id: str, recommendation_id: str) -> Response[dict]:
    """Apply the recommendation to the specified job.

    The basis job can only have tasks that run on the same cluster. That cluster is updated with the
    configuration from the prediction and returned in the result job configuration. Use this function
    to apply a prediction to an existing job or test a prediction with a one-off run.

    :param job_id: basis job ID
    :type job_id: str
    :param project_id: Slingshot project ID
    :type project_id: str
    :param recommendation_id: recommendation ID
    :type recommendation_id: str
    :return: job object with recommendation applied to it
    :rtype: Response[dict]
    """
    job = get_default_client().get_job(job_id)

    if "error_code" in job:
        return Response(error=DatabricksAPIError(**job))

    job_settings = job["settings"]
    tasks = job_settings.get("tasks", [])
    if tasks:
        cluster_response = _get_job_cluster(tasks, job_settings.get("job_clusters", []))
        cluster = cluster_response.result
        if cluster:
            recommendation_cluster_response = get_recommendation_cluster(
                cluster, project_id, recommendation_id
            )
            recommendation_cluster = recommendation_cluster_response.result
            if recommendation_cluster:
                cluster_key = tasks[0].get("job_cluster_key")
                if cluster_key:
                    job_settings["job_clusters"] = [
                        j
                        for j in job_settings["job_clusters"]
                        if j.get("job_cluster_key") != cluster_key
                    ] + [{"job_cluster_key": cluster_key, "new_cluster": recommendation_cluster}]
                else:
                    # For `new_cluster` definitions, Databricks will automatically assign the newly created cluster a name,
                    # and will reject any run submissions where the `cluster_name` is pre-populated
                    if "cluster_name" in recommendation_cluster:
                        del recommendation_cluster["cluster_name"]
                    tasks[0]["new_cluster"] = recommendation_cluster
                return Response(result=job)
            return recommendation_cluster_response
        return cluster_response
    return Response(error=DatabricksError(message="No task found in job"))


def get_recommendation_cluster(
    cluster: dict, project_id: str, recommendation_id: str
) -> Response[dict]:
    """Apply the recommendation to the provided cluster.

    The cluster is updated with configuration from the prediction and returned in the result.

    :param cluster: Databricks cluster object
    :type cluster: dict
    :param project_id: Slingshot project ID
    :type project_id: str
    :param recommendation_id: The id of the recommendation to fetch and apply to the given cluster
    :type recommendation_id: str, optional
    :return: cluster object with prediction applied to it
    :rtype: Response[dict]
    """
    recommendation_response = projects.get_project_recommendation(project_id, recommendation_id)
    recommendation = recommendation_response.result.get("recommendation")
    if recommendation:
        # num_workers/autoscale are mutually exclusive settings, and we are relying on our Prediction
        #  Recommendations to set these appropriately. Since we may recommend a Static cluster (i.e. a cluster
        #  with `num_workers`) for a cluster that was originally autoscaled, we want to make sure to remove this
        #  prior configuration
        cluster.pop("num_workers", None)

        cluster.pop("autoscale", None)

        recommendation_cluster = deep_update(cluster, recommendation["configuration"])

        return Response(result=recommendation_cluster)
    return recommendation_response


def get_project_job(
    job_id: str, project_id: str, region_name: Optional[str] = None
) -> Response[dict]:
    """Apply project configuration to a job.

    The job can only have tasks that run on the same job cluster. That cluster is updated with tags
    and a log configuration to facilitate project continuity. The result can be tested in a
    one-off run or applied to an existing job to surface run-time (see :py:func:`~run_job_object`) or cost optimizations.

    :param job_id: ID of basis job
    :type job_id: str
    :param project_id: Slingshot project ID
    :type project_id: str
    :param region_name: region name, defaults to AWS configuration
    :type region_name: str, optional
    :return: project job object
    :rtype: Response[dict]
    """
    job = get_default_client().get_job(job_id)
    if "error_code" in job:
        return Response(error=DatabricksAPIError(**job))

    job_settings = job["settings"]
    tasks = job_settings.get("tasks", [])
    if tasks:
        cluster_response = _get_job_cluster(tasks, job_settings.get("job_clusters", []))
        cluster = cluster_response.result
        if cluster:
            project_cluster_response = get_project_cluster(
                cluster, project_id, region_name=region_name
            )
            project_cluster = project_cluster_response.result
            if project_cluster:
                cluster_key = tasks[0].get("job_cluster_key")
                if cluster_key:
                    job_settings["job_clusters"] = [
                        j
                        for j in job_settings["job_clusters"]
                        if j.get("job_cluster_key") != cluster_key
                    ] + [{"job_cluster_key": cluster_key, "new_cluster": project_cluster}]
                else:
                    tasks[0]["new_cluster"] = project_cluster

                return Response(result=job)
            return project_cluster_response
        return cluster_response
    return Response(error=DatabricksError(message="No task found in job"))


def get_project_cluster(
    cluster: dict, project_id: str, region_name: Optional[str] = None
) -> Response[dict]:
    """Apply project configuration to a cluster.

    The cluster is updated with tags and a log configuration to facilitate project continuity.

    :param cluster: Databricks cluster object
    :type cluster: dict
    :param project_id: Slingshot project ID
    :type project_id: str
    :param region_name: region name, defaults to AWS configuration
    :type region_name: str, optional
    :return: project job object
    :rtype: Response[dict]
    """
    project_settings_response = get_project_cluster_settings(project_id, region_name=region_name)
    project_cluster_settings = project_settings_response.result
    if project_cluster_settings:
        project_cluster = deep_update(cluster, project_cluster_settings)

        return Response(result=project_cluster)
    return project_settings_response


def get_project_cluster_settings(
    project_id: str, region_name: Optional[str] = None
) -> Response[dict]:
    """Gets cluster configuration for a project.

    This configuration is intended to be used to update the cluster of a Databricks job so that
    its runs can be included in a Slingshot project.

    :param project_id: Slingshot project ID
    :type project_id: str
    :param region_name: region name, defaults to AWS configuration
    :type region_name: str, optional
    :return: project cluster settings - a subset of a Databricks cluster object
    :rtype: Response[dict]
    """
    cluster_template_response = projects.get_project_cluster_template(
        project_id, region_name=region_name
    )
    cluster_template = cluster_template_response.result
    return Response(result=cluster_template)


def _get_job_cluster(tasks: List[dict], job_clusters: list) -> Response[dict]:
    if len(tasks) == 1:
        return _get_task_cluster(tasks[0], job_clusters)

    if [t.get("job_cluster_key") for t in tasks].count(tasks[0].get("job_cluster_key")) == len(
        tasks
    ):
        for cluster in job_clusters:
            if cluster["job_cluster_key"] == tasks[0].get("job_cluster_key"):
                return Response(result=cluster["new_cluster"])
        return Response(error=DatabricksError(message="No cluster found for task"))
    return Response(error=DatabricksError(message="Not all tasks use the same cluster"))


def _get_project_job_clusters(
    job: dict,
    exclude_tasks: Union[Collection[str], None] = None,
) -> Dict[str, Tuple[Tuple[str], dict]]:
    """Returns a mapping of project IDs to cluster paths and clusters.

    Cluster paths are tuples that can be used to locate clusters in a job object, e.g.

    ("tasks", <task_key>) or ("job_clusters", <job_cluster_key>)

    Items for project IDs with more than 1 associated cluster are omitted"""
    job_clusters = {
        c["job_cluster_key"]: c["new_cluster"] for c in job["settings"].get("job_clusters", [])
    }
    all_project_clusters = defaultdict(dict)

    for task in job["settings"]["tasks"]:
        if not exclude_tasks or task["task_key"] not in exclude_tasks:
            task_cluster = task.get("new_cluster")
            if task_cluster:
                task_cluster_path = ("tasks", task["task_key"])

            if not task_cluster:
                task_cluster = job_clusters.get(task.get("job_cluster_key"))
                task_cluster_path = ("job_clusters", task.get("job_cluster_key"))

            if task_cluster:
                cluster_project_id = task_cluster.get("custom_tags", {}).get("slingshot:project-id")
                all_project_clusters[cluster_project_id][task_cluster_path] = task_cluster

    filtered_project_clusters = {}
    for project_id, clusters in all_project_clusters.items():
        if len(clusters) > 1:
            logger.warning(f"More than 1 cluster found for project ID {project_id}")
        else:
            filtered_project_clusters[project_id] = next(iter(clusters.items()))

    return filtered_project_clusters


def _get_task_cluster(task: dict, clusters: list) -> Response[dict]:
    cluster = task.get("new_cluster")

    if not cluster:
        cluster_matches = [
            candidate
            for candidate in clusters
            if candidate["job_cluster_key"] == task.get("job_cluster_key")
        ]
        if cluster_matches:
            cluster = cluster_matches[0]["new_cluster"]
        else:
            return Response(error=DatabricksError(message="No cluster found for task"))
    return Response(result=cluster)
