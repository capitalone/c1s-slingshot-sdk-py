from unittest import TestCase
from unittest.mock import patch

from slingshot.api.projects import (
    create_project,
    create_project_recommendation,
    get_cluster_definition_and_recommendation,
    get_latest_project_config_recommendation,
    get_products,
    get_project,
    get_project_by_app_id,
    get_project_cluster_template,
    get_submissions,
    get_updated_cluster_definition,
    update_project,
)
from slingshot.models import ProjectError, RecommendationError, Response
from tests.conftest import get_aws_rec_from_file, get_azure_rec_from_file, get_project_from_file


class TestSlingshot(TestCase):
    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_get_latest_aws_project_config_recommendation(self, mock_send):
        mock_send.return_value = get_aws_rec_from_file()
        expected_result = Response(
            result={
                "node_type_id": "i6.xlarge",
                "driver_node_type_id": "i6.xlarge",
                "custom_tags": {
                    "slingshot:project-id": "b9bd7136-7699-4603-9040-c6dc4c914e43",
                    "slingshot:run-id": "e96401da-f64d-4ed0-8ded-db1317f40248",
                    "slingshot:recommendation-id": "e029a220-c6a5-49fd-b7ed-7ea046366741",
                    "slingshot:tenant-id": "352176a7-b605-4cc2-b3b2-ee591715b6b4",
                },
                "num_workers": 20,
                # SLI-19250 Confirm this is the right spark_conf
                "spark_conf": {"spark.databricks.isv.product": "slingshot-gradient"},
                "spark_version": "13.3.x-scala2.12",
                "runtime_engine": "PHOTON",
                "aws_attributes": {
                    "first_on_demand": 1,
                    "availability": "SPOT_WITH_FALLBACK",
                    "spot_bid_price_percent": 100,
                },
            }
        )

        result = get_latest_project_config_recommendation("project_id")
        assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_get_latest_azure_project_config_recommendation(self, mock_send):
        mock_send.return_value = get_azure_rec_from_file()
        expected_result = Response(
            result={
                "node_type_id": "Standard_D4s_v3",
                "driver_node_type_id": "Standard_D4s_v3",
                "custom_tags": {
                    "slingshot:project-id": "769c3443-afd7-45ff-a72a-27bf4296b80e",
                    "slingshot:run-id": "d3f8db6c-df4b-430a-a511-a1e9c95d1ad0",
                    "slingshot:recommendation-id": "6024acdd-fd13-4bf1-82f5-44f1ab7008f2",
                    "slingshot:tenant-id": "290d381e-8eb4-4d6a-80d4-453d82897ecc",
                },
                "num_workers": 5,
                # SLI-19250 Confirm this is the right spark_conf
                "spark_conf": {"spark.databricks.isv.product": "slingshot-gradient"},
                "spark_version": "13.3.x-scala2.12",
                "runtime_engine": "STANDARD",
                "azure_attributes": {
                    "availability": "SPOT_WITH_FALLBACK_AZURE",
                    "first_on_demand": 7,
                    "spot_bid_max_price": 100.0,
                },
            }
        )

        result = get_latest_project_config_recommendation("project_id")
        assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_get_cluster_definition_no_recommendation(self, mock_send):
        mock_send.return_value = {"result": []}
        expected_result = Response(error=RecommendationError(message="Recommendation failed"))

        with open("tests/test_files/azure_cluster.json") as cluster_in:
            result = get_cluster_definition_and_recommendation("project_id", cluster_in.read())
            assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_get_cluster_definition_and_recommendation(self, mock_send):
        mock_send.return_value = get_aws_rec_from_file()

        expected_result = Response(
            result={
                "cluster_recommendation": {
                    "node_type_id": "i6.xlarge",
                    "driver_node_type_id": "i6.xlarge",
                    "custom_tags": {
                        "slingshot:project-id": "b9bd7136-7699-4603-9040-c6dc4c914e43",
                        "slingshot:run-id": "e96401da-f64d-4ed0-8ded-db1317f40248",
                        "slingshot:recommendation-id": "e029a220-c6a5-49fd-b7ed-7ea046366741",
                        "slingshot:tenant-id": "352176a7-b605-4cc2-b3b2-ee591715b6b4",
                    },
                    "num_workers": 20,
                    # SLI-19250 Confirm this is the right spark_conf
                    "spark_conf": {"spark.databricks.isv.product": "slingshot-gradient"},
                    "spark_version": "13.3.x-scala2.12",
                    "runtime_engine": "PHOTON",
                    "aws_attributes": {
                        "first_on_demand": 1,
                        "availability": "SPOT_WITH_FALLBACK",
                        "spot_bid_price_percent": 100,
                    },
                },
                "cluster_definition": {
                    "cluster_id": "1234-567890-reef123",
                    "spark_context_id": 4020997813441462000,
                    "cluster_name": "my-cluster",
                    "spark_version": "13.3.x-scala2.12",
                    "aws_attributes": {
                        "zone_id": "us-west-2c",
                        "first_on_demand": 1,
                        "availability": "SPOT_WITH_FALLBACK",
                        "spot_bid_price_percent": 100,
                        "ebs_volume_count": 0,
                    },
                    "node_type_id": "i3.xlarge",
                    "driver_node_type_id": "i3.xlarge",
                    "autotermination_minutes": 120,
                    "enable_elastic_disk": False,
                    "disk_spec": {"disk_count": 0},
                    "cluster_source": "UI",
                    "enable_local_disk_encryption": False,
                    "instance_source": {"node_type_id": "i3.xlarge"},
                    "driver_instance_source": {"node_type_id": "i3.xlarge"},
                    "state": "TERMINATED",
                    "state_message": "Inactive cluster terminated (inactive for 120 minutes).",
                    "start_time": 1618263108824,
                    "terminated_time": 1619746525713,
                    "last_state_loss_time": 1619739324740,
                    "num_workers": 30,
                    "default_tags": {
                        "Vendor": "Databricks",
                        "Creator": "someone@example.com",
                        "ClusterName": "my-cluster",
                        "ClusterId": "1234-567890-reef123",
                    },
                    "creator_user_name": "someone@example.com",
                    "termination_reason": {
                        "code": "INACTIVITY",
                        "parameters": {"inactivity_duration_min": "120"},
                        "type": "SUCCESS",
                    },
                    "init_scripts_safe_mode": False,
                    "spec": {"spark_version": "13.3.x-scala2.12"},
                },
            }
        )

        with open("tests/test_files/aws_cluster.json") as cluster_in:
            result = get_cluster_definition_and_recommendation("project_id", cluster_in.read())
            assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient.get_latest_project_recommendation")
    def test_get_updated_aws_cluster_definition(self, mock_send):
        mock_send.return_value = get_aws_rec_from_file()

        expected_result = Response(
            result={
                "cluster_id": "1234-567890-reef123",
                "spark_context_id": 4020997813441462000,
                "cluster_name": "my-cluster",
                "spark_version": "13.3.x-scala2.12",
                "aws_attributes": {
                    "first_on_demand": 1,
                    "ebs_volume_count": 0,
                    "availability": "SPOT_WITH_FALLBACK",
                    "spot_bid_price_percent": 100,
                    "zone_id": "us-west-2c",
                },
                "custom_tags": {
                    "slingshot:project-id": "b9bd7136-7699-4603-9040-c6dc4c914e43",
                    "slingshot:run-id": "e96401da-f64d-4ed0-8ded-db1317f40248",
                    "slingshot:recommendation-id": "e029a220-c6a5-49fd-b7ed-7ea046366741",
                    "slingshot:tenant-id": "352176a7-b605-4cc2-b3b2-ee591715b6b4",
                },
                "node_type_id": "i6.xlarge",
                "driver_node_type_id": "i6.xlarge",
                "autotermination_minutes": 120,
                "enable_elastic_disk": False,
                "disk_spec": {"disk_count": 0},
                "cluster_source": "UI",
                "enable_local_disk_encryption": False,
                "instance_source": {"node_type_id": "i3.xlarge"},
                "driver_instance_source": {"node_type_id": "i3.xlarge"},
                # SLI-19250 Confirm this is the right spark_conf
                "spark_conf": {"spark.databricks.isv.product": "slingshot-gradient"},
                "state": "TERMINATED",
                "state_message": "Inactive cluster terminated (inactive for 120 minutes).",
                "start_time": 1618263108824,
                "terminated_time": 1619746525713,
                "last_state_loss_time": 1619739324740,
                "num_workers": 20,
                "runtime_engine": "PHOTON",
                "default_tags": {
                    "Vendor": "Databricks",
                    "Creator": "someone@example.com",
                    "ClusterName": "my-cluster",
                    "ClusterId": "1234-567890-reef123",
                },
                "creator_user_name": "someone@example.com",
                "termination_reason": {
                    "code": "INACTIVITY",
                    "parameters": {"inactivity_duration_min": "120"},
                    "type": "SUCCESS",
                },
                "init_scripts_safe_mode": False,
                "spec": {"spark_version": "13.3.x-scala2.12"},
            }
        )

        with open("tests/test_files/aws_cluster.json") as cluster_in:
            result = get_updated_cluster_definition("project_id", cluster_in.read())
            assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient.get_latest_project_recommendation")
    def test_get_updated_azure_cluster_definition(self, mock_send):
        mock_send.return_value = get_azure_rec_from_file()

        expected_result = Response(
            result={
                "cluster_id": "1114-202840-mu1ql9xp",
                "spark_context_id": 8637481617925571639,
                "cluster_name": "my-cluster",
                "spark_version": "13.3.x-scala2.12",
                "azure_attributes": {
                    "first_on_demand": 7,
                    "availability": "SPOT_WITH_FALLBACK_AZURE",
                    "spot_bid_max_price": 100.0,
                },
                "node_type_id": "Standard_D4s_v3",
                "driver_node_type_id": "Standard_D4s_v3",
                "autotermination_minutes": 120,
                "enable_elastic_disk": False,
                "disk_spec": {"disk_count": 0},
                "cluster_source": "UI",
                "enable_local_disk_encryption": False,
                "instance_source": {"node_type_id": "Standard_DS5_v2"},
                "driver_instance_source": {"node_type_id": "Standard_DS5_v2"},
                "state": "TERMINATED",
                "state_message": "Inactive cluster terminated (inactive for 120 minutes).",
                "start_time": 1618263108824,
                "terminated_time": 1619746525713,
                "last_state_loss_time": 1619739324740,
                "num_workers": 5,
                "default_tags": {
                    "Vendor": "Databricks",
                    "Creator": "someone@example.com",
                    "ClusterName": "my-cluster",
                    "ClusterId": "1234-567890-reef123",
                },
                "creator_user_name": "someone@example.com",
                "termination_reason": {
                    "code": "INACTIVITY",
                    "parameters": {"inactivity_duration_min": "120"},
                    "type": "SUCCESS",
                },
                "init_scripts_safe_mode": False,
                "spec": {"spark_version": "13.3.x-scala2.12"},
                "custom_tags": {
                    "slingshot:project-id": "769c3443-afd7-45ff-a72a-27bf4296b80e",
                    "slingshot:run-id": "d3f8db6c-df4b-430a-a511-a1e9c95d1ad0",
                    "slingshot:recommendation-id": "6024acdd-fd13-4bf1-82f5-44f1ab7008f2",
                    "slingshot:tenant-id": "290d381e-8eb4-4d6a-80d4-453d82897ecc",
                },
                # SLI-19250 Confirm this is the right spark_conf
                "spark_conf": {"spark.databricks.isv.product": "slingshot-gradient"},
                "runtime_engine": "STANDARD",
            }
        )

        with open("tests/test_files/azure_cluster.json") as cluster_in:
            result = get_updated_cluster_definition("project_id", cluster_in.read())
            assert result == expected_result

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_create_project(self, mock_send):
        mock_send.return_value = get_project_from_file()
        test_create_project_response = Response(
            result={
                "app_id": None,
                "auto_apply_recs": False,
                "cluster_log_url": None,
                "cluster_path": "jobs_cluster/Test_Jobs_Cluster",
                "description": "project-description",
                "id": "project-id",
                "job_id": "109871920",
                "name": "project-name",
                "optimize_instance_size": False,
                "prediction_params": None,
                "product_code": "aws-databricks",
                "workspace_id": "10391894027",
            }
        )

        response = create_project(
            name="project-name", product_code="aws-databricks", description="project-description"
        )

        assert response == test_create_project_response
        assert response.error is None

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_get_products(self, mock_send):
        supported_products = ["aws-databricks", "azure-databricks", "gcp-databricks"]
        # Mock the client response
        mock_send.return_value = {"result": supported_products}

        response = get_products()

        assert response.result == supported_products
        assert response.error is None

    @patch("slingshot.clients.slingshot.SlingshotClient._send")
    def test_update_project(self, mock_send):
        mock_send.return_value = get_project_from_file()
        test_update_project_response = Response(
            result={
                "app_id": None,
                "auto_apply_recs": False,
                "cluster_log_url": None,
                "cluster_path": "jobs_cluster/Test_Jobs_Cluster",
                "description": "project-description",
                "id": "project-id",
                "job_id": "109871920",
                "name": "project-name",
                "optimize_instance_size": False,
                "prediction_params": None,
                "product_code": "aws-databricks",
                "workspace_id": "10391894027",
            }
        )

        response = update_project(
            project_id="project-id",
            description="project-name",
            job_id="aws-databricks",
            auto_apply_recs=True,
        )

        assert response == test_update_project_response
        assert response.error is None

    @patch("slingshot.api.projects.get_default_client")
    def test_get_project_cluster_template(self, mock_client):
        # Mock the client response
        mock_response = {"result": {"template": "cluster_template"}}
        mock_client.return_value.get_project_cluster_template.return_value = mock_response

        # Call the function
        response = get_project_cluster_template("project_id", region_name="us-west-2")

        # Assertions
        mock_client.return_value.get_project_cluster_template.assert_called_once_with(
            "project_id", params={"aws_region": "us-west-2"}
        )
        self.assertIsInstance(response, Response)
        self.assertEqual(response.result, {"template": "cluster_template"})

    @patch("slingshot.api.projects.get_default_client")
    def test_get_project_by_app_id_success(self, mock_client):
        # Mock the client response
        mock_response = {"result": [{"id": "project_1"}]}
        mock_client.return_value.get_projects.return_value = mock_response

        # Call the function
        response = get_project_by_app_id("app_id_123")

        # Assertions
        mock_client.return_value.get_projects.assert_called_once_with({"app_id": "app_id_123"})
        self.assertIsInstance(response, Response)
        self.assertEqual(response.result, {"id": "project_1"})

    @patch("slingshot.api.projects.get_default_client")
    def test_get_project_by_app_id_no_project_found(self, mock_client):
        # Mock the client response
        mock_response = {"result": []}
        mock_client.return_value.get_projects.return_value = mock_response

        # Call the function
        response = get_project_by_app_id("app_id_123")

        # Assertions
        mock_client.return_value.get_projects.assert_called_once_with({"app_id": "app_id_123"})
        self.assertIsInstance(response, Response)
        self.assertIsInstance(response.error, ProjectError)
        self.assertEqual(str(response.error), "Project Error: No project found for 'app_id_123'")

    @patch("slingshot.api.projects.get_default_client")
    def test_get_submissions(self, mock_client):
        # Mock the client response
        mock_response = {"items": [{"submission_id": "submission_1"}]}
        mock_client.return_value.get_project_submissions.return_value = mock_response

        # Call the function
        response = get_submissions("project_id_123")

        # Assertions
        mock_client.return_value.get_project_submissions.assert_called_once_with("project_id_123")
        self.assertIsInstance(response, Response)
        self.assertEqual(response.result, [{"submission_id": "submission_1"}])

    @patch("slingshot.api.projects.get_default_client")
    def test_get_submissions_no_items(self, mock_client):
        # Mock the client response
        mock_response = {"items": []}
        mock_client.return_value.get_project_submissions.return_value = mock_response

        # Call the function
        response = get_submissions("project_id_123")

        # Assertions
        mock_client.return_value.get_project_submissions.assert_called_once_with("project_id_123")
        self.assertIsNone(response)

    @patch("slingshot.api.projects.get_default_client")
    def test_create_project_recommendation_success(self, mock_client):
        # Mock the client response
        mock_response = {"result": {"id": "recommendation_123"}}
        mock_client.return_value.create_project_recommendation.return_value = mock_response

        # Call the function
        response = create_project_recommendation("project_id_123", param1="value1")

        # Assertions
        mock_client.return_value.create_project_recommendation.assert_called_once_with(
            "project_id_123", param1="value1"
        )
        self.assertIsInstance(response, Response)
        self.assertEqual(response.result, "recommendation_123")

    @patch("slingshot.api.projects.get_default_client")
    def test_create_project_recommendation_error(self, mock_client):
        # Mock the client response
        mock_response = {
            "error": {"message": "Error creating recommendation", "code": "BAD REQUEST"}
        }
        mock_client.return_value.create_project_recommendation.return_value = mock_response

        # Call the function
        response = create_project_recommendation("project_id_123")

        # Assertions
        mock_client.return_value.create_project_recommendation.assert_called_once_with(
            "project_id_123"
        )
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.message, "Error creating recommendation")

    @patch("slingshot.api.projects.get_default_client")
    def test_get_project_success(self, mock_client):
        # Mock the client response
        mock_response = {"result": {"id": "project_123", "name": "Test Project"}}
        mock_client.return_value.get_project.return_value = mock_response

        # Call the function
        response = get_project("project_id_123")

        # Assertions
        mock_client.return_value.get_project.assert_called_once_with("project_id_123", params=None)
        self.assertIsInstance(response, Response)
        self.assertEqual(response.result, {"id": "project_123", "name": "Test Project"})

    @patch("slingshot.api.projects.get_default_client")
    def test_get_project_error(self, mock_client):
        # Mock the client response
        mock_response = {"error": {"message": "Project not found", "code": "NOT FOUND"}}
        mock_client.return_value.get_project.return_value = mock_response

        # Call the function
        response = get_project("project_id_123")

        # Assertions
        mock_client.return_value.get_project.assert_called_once_with("project_id_123", params=None)
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.message, "Project not found")
