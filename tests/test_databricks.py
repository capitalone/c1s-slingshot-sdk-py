from unittest.mock import MagicMock, patch

from slingshot._databricks import (
    _get_job_cluster,
    _get_project_job_clusters,
    _get_task_cluster,
    apply_project_recommendation,
    create_and_apply_project_recommendation,
    get_project_cluster,
    get_project_cluster_settings,
    get_project_job,
    get_recommendation_cluster,
    get_recommendation_job,
)
from slingshot.models import DatabricksError, Response
from tests.conftest import get_job_from_file


@patch("slingshot._databricks.projects.create_project_recommendation")
@patch("slingshot._databricks.projects.wait_for_recommendation")
@patch("slingshot._databricks.apply_project_recommendation")
def test_create_and_apply_project_recommendation_success(
    mock_apply_project_recommendation,
    mock_wait_for_recommendation,
    mock_create_project_recommendation,
):
    # Mock successful responses
    mock_create_project_recommendation.return_value = Response(result="recommendation-id")
    mock_wait_for_recommendation.return_value = Response(result="")
    mock_apply_project_recommendation.return_value = Response(result="recommendation-id")

    response = create_and_apply_project_recommendation("project-id", "job-id")

    assert response.result == "recommendation-id"
    assert response.error is None
    mock_create_project_recommendation.assert_called_once_with("project-id")
    mock_wait_for_recommendation.assert_called_once_with("project-id", "recommendation-id")
    mock_apply_project_recommendation.assert_called_once_with(
        "job-id", "project-id", "recommendation-id"
    )


@patch("slingshot._databricks.projects.create_project_recommendation")
def test_create_and_apply_project_recommendation_create_error(mock_create_project_recommendation):
    # Mock an error response from create_project_recommendation
    mock_create_project_recommendation.return_value = Response(
        error=DatabricksError(message="Error creating recommendation")
    )

    response = create_and_apply_project_recommendation("project-id", "job-id")

    assert response.result is None
    assert isinstance(response.error, DatabricksError)
    mock_create_project_recommendation.assert_called_once_with("project-id")


@patch("slingshot._databricks.projects.create_project_recommendation")
@patch("slingshot._databricks.projects.wait_for_recommendation")
def test_create_and_apply_project_recommendation_wait_error(
    mock_wait_for_recommendation, mock_create_project_recommendation
):
    # Mock successful creation but error in waiting
    mock_create_project_recommendation.return_value = Response(result="recommendation-id")
    mock_wait_for_recommendation.return_value = Response(
        error=DatabricksError(message="Error waiting for recommendation")
    )

    response = create_and_apply_project_recommendation("project-id", "job-id")

    assert response.result is None
    assert isinstance(response.error, DatabricksError)
    mock_create_project_recommendation.assert_called_once_with("project-id")
    mock_wait_for_recommendation.assert_called_once_with("project-id", "recommendation-id")


@patch("slingshot._databricks.get_default_client")
@patch("slingshot._databricks.get_recommendation_cluster")
@patch("slingshot._databricks._get_project_job_clusters")
def test_apply_project_recommendation_success(
    mock_get_project_job_clusters, mock_get_recommendation_cluster, mock_get_default_client
):
    # Mock the Databricks client and responses
    mock_client = MagicMock()
    mock_client.get_job.return_value = get_job_from_file()
    mock_client.update_job.return_value = {}
    mock_get_default_client.return_value = mock_client

    mock_get_project_job_clusters.return_value = {
        "project-id": (("job_clusters", "cluster-key"), {"cluster": "definition"})
    }
    mock_get_recommendation_cluster.return_value = Response(result={"new_cluster": "definition"})

    response = apply_project_recommendation("job-id", "project-id", "recommendation-id")

    assert response.result == "recommendation-id"
    assert response.error is None
    mock_client.get_job.assert_called_once_with("job-id")
    mock_client.update_job.assert_called_once()
    mock_get_project_job_clusters.assert_called_once()
    mock_get_recommendation_cluster.assert_called_once_with(
        {"cluster": "definition"}, "project-id", "recommendation-id"
    )


@patch("slingshot._databricks.get_default_client")
@patch("slingshot._databricks.get_recommendation_cluster")
@patch("slingshot._databricks._get_project_job_clusters")
def test_apply_project_recommendation_cluster_not_found(
    mock_get_project_job_clusters, mock_get_recommendation_cluster, mock_get_default_client
):
    # Mock the Databricks client and responses
    mock_client = MagicMock()
    mock_client.get_job.return_value = get_job_from_file()
    mock_get_default_client.return_value = mock_client

    mock_get_project_job_clusters.return_value = {}

    response = apply_project_recommendation("job-id", "project-id", "recommendation-id")

    assert response.result is None
    assert isinstance(response.error, DatabricksError)
    mock_client.get_job.assert_called_once_with("job-id")
    mock_get_project_job_clusters.assert_called_once()
    mock_get_recommendation_cluster.assert_not_called()


@patch("slingshot._databricks.get_default_client")
@patch("slingshot.api.projects.get_project_recommendation")
@patch("slingshot._databricks._get_job_cluster")
def test_get_recommendation_job_success(
    mock_get_job_cluster, mock_get_recommendation_cluster, mock_get_default_client
):
    # Mock the Databricks client and responses
    mock_client = MagicMock()
    mock_client.get_job.return_value = get_job_from_file()
    mock_get_default_client.return_value = mock_client

    mock_get_job_cluster.return_value = Response(result={"cluster_key": "job_cluster_key"})
    mock_get_recommendation_cluster.return_value = Response(
        result={
            "recommendation": {
                "configuration": {
                    "autoscale": {"max_workers": 10, "min_workers": 2},
                    "node_type_id": "i3.xlarge",
                    "spark_conf": {"spark.speculation": True},
                    "spark_version": "7.3.x-scala2.12",
                }
            }
        }
    )

    response = get_recommendation_job("job-id", "project-id", "recommendation-id")

    assert response.result["settings"]["tasks"][0]["new_cluster"] == {
        "autoscale": {"max_workers": 10, "min_workers": 2},
        "node_type_id": "i3.xlarge",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
        "cluster_key": "job_cluster_key",
    }
    assert response.error is None
    mock_client.get_job.assert_called_once_with("job-id")
    mock_get_job_cluster.assert_called_once()
    mock_get_recommendation_cluster.assert_called_once_with("project-id", "recommendation-id")


@patch("slingshot._databricks.projects.get_project_recommendation")
def test_get_recommendation_cluster_success(mock_get_project_recommendation):
    # Mock the project recommendation response
    mock_get_project_recommendation.return_value = Response(
        result={
            "recommendation": {
                "configuration": {
                    "num_workers": 5,
                    "node_type_id": "r5.large",
                    "spark_conf": {"spark.speculation": True},
                    "spark_version": "7.3.x-scala2.12",
                }
            }
        }
    )

    cluster = {
        "autoscale": {"max_workers": 10, "min_workers": 2},
        "node_type_id": "i3.xlarge",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
    }
    response = get_recommendation_cluster(cluster, "project-id", "recommendation-id")

    assert response.result == {
        "num_workers": 5,
        "node_type_id": "r5.large",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
    }
    assert response.error is None
    mock_get_project_recommendation.assert_called_once_with("project-id", "recommendation-id")


@patch("slingshot._databricks.get_default_client")
@patch("slingshot._databricks.get_project_cluster")
@patch("slingshot._databricks._get_job_cluster")
def test_get_project_job_success(
    mock_get_job_cluster, mock_get_project_cluster, mock_get_default_client
):
    # Mock the Databricks client and responses
    mock_client = MagicMock()
    mock_client.get_job.return_value = get_job_from_file()
    mock_get_default_client.return_value = mock_client

    mock_get_project_cluster.return_value = Response(
        result={
            "autoscale": {"max_workers": 16, "min_workers": 2},
            "node_type_id": "r4.xlarge",
            "spark_conf": {"spark.speculation": True},
            "spark_version": "7.3.x-scala2.12",
            "custom_tags": {"slingshot:project-id": "proj1"},
            "cluster_log_conf": {"dbfs": {"destination": "dbfs:/logs"}},
        }
    )

    response = get_project_job("job-id", "project-id")

    assert response.result["settings"]["tasks"][0]["new_cluster"] == {
        "autoscale": {"max_workers": 16, "min_workers": 2},
        "node_type_id": "r4.xlarge",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
        "custom_tags": {"slingshot:project-id": "proj1"},
        "cluster_log_conf": {"dbfs": {"destination": "dbfs:/logs"}},
    }
    assert response.error is None
    mock_client.get_job.assert_called_once_with("job-id")
    mock_get_job_cluster.assert_called_once()
    mock_get_project_cluster.assert_called_once()


@patch("slingshot._databricks.get_project_cluster_settings")
def test_get_project_cluster_success(mock_get_project_cluster_settings):
    # Mock the project cluster settings response
    mock_get_project_cluster_settings.return_value = Response(
        result={
            "custom_tags": {"slingshot:project-id": "proj1"},
            "cluster_log_conf": {"dbfs": {"destination": "dbfs:/logs"}},
        },
    )

    cluster = {
        "autoscale": {"max_workers": 16, "min_workers": 2},
        "node_type_id": "r4.xlarge",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
    }
    response = get_project_cluster(cluster, "project-id")

    assert response.result == {
        "autoscale": {"max_workers": 16, "min_workers": 2},
        "node_type_id": "r4.xlarge",
        "spark_conf": {"spark.speculation": True},
        "spark_version": "7.3.x-scala2.12",
        "custom_tags": {"slingshot:project-id": "proj1"},
        "cluster_log_conf": {"dbfs": {"destination": "dbfs:/logs"}},
    }
    assert response.error is None
    mock_get_project_cluster_settings.assert_called_once_with("project-id", region_name=None)


@patch("slingshot._databricks.projects.get_project_cluster_template")
def test_get_project_cluster_settings_success(mock_get_project_cluster_template):
    # Mock the project cluster template response
    mock_get_project_cluster_template.return_value = Response(
        result={
            "custom_tags": {"slingshot:project-id": "proj1"},
            "cluster_log_conf": {"dbfs": {"destination": "dbfs:/logs"}},
        },
    )

    response = get_project_cluster_settings("project-id")

    assert response.error is None
    mock_get_project_cluster_template.assert_called_once_with("project-id", region_name=None)


def test_get_task_cluster_with_new_cluster():
    task = {"new_cluster": {"cluster_key": "value"}}
    clusters = []

    response = _get_task_cluster(task, clusters)

    assert response.result == {"cluster_key": "value"}
    assert response.error is None


def test_get_task_cluster_with_matching_cluster():
    task = {"job_cluster_key": "key1"}
    clusters = [{"job_cluster_key": "key1", "new_cluster": {"cluster_key": "value"}}]

    response = _get_task_cluster(task, clusters)

    assert response.result == {"cluster_key": "value"}
    assert response.error is None


def test_get_task_cluster_no_matching_cluster():
    task = {"job_cluster_key": "key1"}
    clusters = [{"job_cluster_key": "key2", "new_cluster": {"cluster_key": "value"}}]

    response = _get_task_cluster(task, clusters)

    assert response.result is None
    assert isinstance(response.error, DatabricksError)


def test_get_job_cluster_single_task():
    tasks = [{"new_cluster": {"cluster_key": "value"}}]
    job_clusters = []

    response = _get_job_cluster(tasks, job_clusters)

    assert response.result == {"cluster_key": "value"}
    assert response.error is None


def test_get_job_cluster_same_cluster_key():
    tasks = [{"job_cluster_key": "key1"}, {"job_cluster_key": "key1"}]
    job_clusters = [{"job_cluster_key": "key1", "new_cluster": {"cluster_key": "value"}}]

    response = _get_job_cluster(tasks, job_clusters)

    assert response.result == {"cluster_key": "value"}
    assert response.error is None


def test_get_job_cluster_different_cluster_keys():
    tasks = [{"job_cluster_key": "key1"}, {"job_cluster_key": "key2"}]
    job_clusters = [{"job_cluster_key": "key1", "new_cluster": {"cluster_key": "value"}}]

    response = _get_job_cluster(tasks, job_clusters)

    assert response.result is None
    assert isinstance(response.error, DatabricksError)


def test_get_project_job_clusters_multiple_tasks():
    job = {
        "settings": {
            "tasks": [
                {
                    "task_key": "task1",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj1"}},
                },
                {"task_key": "task2", "job_cluster_key": "key1"},
            ],
            "job_clusters": [
                {
                    "job_cluster_key": "key1",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj2"}},
                }
            ],
        }
    }

    response = _get_project_job_clusters(job)

    assert "proj1" in response
    assert "proj2" in response
    assert response["proj1"][0] == ("tasks", "task1")
    assert response["proj2"][0] == ("job_clusters", "key1")


def test_get_project_job_clusters_with_exclude_tasks():
    job = {
        "settings": {
            "tasks": [
                {
                    "task_key": "task1",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj1"}},
                },
                {"task_key": "task2", "job_cluster_key": "key1"},
            ],
            "job_clusters": [
                {
                    "job_cluster_key": "key1",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj2"}},
                }
            ],
        }
    }

    response = _get_project_job_clusters(job, exclude_tasks=["task1"])

    assert "proj1" not in response
    assert "proj2" in response
    assert response["proj2"][0] == ("job_clusters", "key1")


def test_get_project_job_clusters_multiple_clusters_per_project():
    job = {
        "settings": {
            "tasks": [
                {
                    "task_key": "task1",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj1"}},
                },
                {
                    "task_key": "task2",
                    "new_cluster": {"custom_tags": {"slingshot:project-id": "proj1"}},
                },
            ]
        }
    }

    response = _get_project_job_clusters(job)

    assert "proj1" not in response  # Should be omitted due to multiple clusters
