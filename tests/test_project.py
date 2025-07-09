import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient
from slingshot.exceptions import ResourceNotFoundError


def test_get_project_success(httpx_mock: HTTPXMock, client: SlingshotClient) -> None:
    """Test fetching a project by its ID."""
    project_id = "project_id_123"
    mock_response = {"id": "project_id_123"}
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/v1/projects/{project_id}",
        status_code=200,
        json=mock_response,
    )
    project = client.projects.get_project(project_id=project_id)
    assert project["id"] == project_id


def test_get_project_missing(httpx_mock: HTTPXMock, client: SlingshotClient) -> None:
    """Test error handling when fetching a project."""
    project_id = "project_id_123"
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/v1/projects/{project_id}",
        status_code=404,
        json={"error": "Project not found"},
    )
    with pytest.raises(ResourceNotFoundError, match="project_id_123") as exc_info:
        client.projects.get_project(project_id=project_id)
    assert str(exc_info.value) == "Project with identifier 'project_id_123' not found."


@pytest.mark.parametrize(
    "status_code",
    [500, 502, 503, 504, 429],
)
def test_get_project_retries_status_code(
    httpx_mock: HTTPXMock, client: SlingshotClient, status_code: int
) -> None:
    """Test retries on acceptable status code."""
    project_id = "project_id_123"
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/v1/projects/{project_id}",
        status_code=status_code,
        json={"error": "Service unavailable"},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/v1/projects/{project_id}",
        status_code=200,
        json={"id": project_id},
    )
    project = client.projects.get_project(project_id=project_id)
    assert project["id"] == project_id
