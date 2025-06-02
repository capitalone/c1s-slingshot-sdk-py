from unittest.mock import MagicMock, patch

from slingshot.api.workspace import onboard_job


@patch("slingshot.api.workspace.get_default_client")
def test_onboard_job_success(mock_get_default_client):
    # Mock the client and its onboard_workflow method
    mock_client = MagicMock()
    mock_client.onboard_workflow.return_value = {"result": "onboarded-job-id"}
    mock_get_default_client.return_value = mock_client

    response = onboard_job("workspace-id", "job-id", "project-id")

    assert response.result == "onboarded-job-id"
    assert response.error is None
    mock_client.onboard_workflow.assert_called_once_with("workspace-id", "job-id", "project-id")


@patch("slingshot.api.workspace.get_default_client")
def test_onboard_job_error(mock_get_default_client):
    # Mock the client and its onboard_workflow method to return an error
    mock_client = MagicMock()
    mock_client.onboard_workflow.return_value = {
        "error": {"code": "422", "message": "Failed to onboard job"}
    }
    mock_get_default_client.return_value = mock_client

    response = onboard_job("workspace-id", "job-id", "project-id")

    assert response.error
    mock_client.onboard_workflow.assert_called_once_with("workspace-id", "job-id", "project-id")
