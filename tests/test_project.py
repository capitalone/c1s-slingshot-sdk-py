import re

import httpx
import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient
from slingshot.types import Page, ProjectSchema


def test_create_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test creating a project successfully."""
    project_id = "project_id_123"
    project_name = "project_create"
    mock_response = {"result": {"id": project_id, "name": project_name}}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects",
    )
    httpx_mock.add_response(
        method="POST",
        url=url,
        status_code=200,
        json=mock_response,
    )
    project = client.projects.create(
        name=project_name,
        settings={"sla_minutes": 5},
        app_id="test",
    )
    assert "id" in project
    assert project["id"] == project_id
    assert "name" in project
    assert project["name"] == project_name


def test_create_failure(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test creating a project failure."""
    project_name = "project_create"
    mock_error = {"error": "Project cannot be created"}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects",
    )
    httpx_mock.add_response(
        method="POST",
        url=url,
        status_code=404,
        json=mock_error,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.create(name=project_name)
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error


def test_update_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test updating a project successfully."""
    project_id = "project_id_123"
    project_name = "project_update"
    mock_response = {"result": {"id": project_id, "name": project_name}}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects/{project_id}",
    )
    httpx_mock.add_response(
        method="PUT",
        url=url,
        status_code=200,
        json=mock_response,
    )
    project = client.projects.update(
        project_id=project_id,
        name=project_name,
        settings={"sla_minutes": 5},
    )
    assert "id" in project
    assert project["id"] == project_id
    assert "name" in project
    assert project["name"] == project_name


def test_update_failure(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test updating a project failure."""
    project_id = "project_id_123"
    mock_error = {"error": "Project cannot be updated"}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects/{project_id}",
    )
    httpx_mock.add_response(
        method="PUT",
        url=url,
        status_code=404,
        json=mock_error,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.update(
            project_id=project_id,
        )
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error


def test_get_projects_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project list fetching success."""
    creator_id = "test_creator"
    include = ["id"]
    app_id = "test"
    mock_response = {
        "items": [
            {"id": "project_id_123"},
            {"id": "project_id_345"},
        ],
        "page": 2,
        "pages": 2,
    }
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects",
        params={
            "include": include,
            "page": 2,
            "size": 25,
            "creator_id": creator_id,
            "app_id": app_id,
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=url,
        status_code=200,
        json=mock_response,
    )

    response_page: Page[ProjectSchema] = client.projects.get_projects(
        creator_id=creator_id,
        include=include,
        app_id=app_id,
        page=2,
        size=25,
    )
    assert response_page is not None
    assert response_page["items"] == mock_response["items"]
    assert response_page["page"] == 2
    assert response_page["pages"] == 2


def test_get_projects_failure(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project list fetching failure."""
    creator_id = "test_creator"
    include = []
    mock_error = {"error": "Projects cannot be retrieved"}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects",
        params={
            "include": include,
            "page": 1,
            "size": 50,
            "creator_id": creator_id,
        },
    )
    httpx_mock.add_response(method="GET", url=url, status_code=404, json=mock_error)
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.get_projects(
            creator_id=creator_id,
            include=include,
        )
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error


def test_iterate_projects(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project list fetching page iteration."""
    creator_id = "test_creator"
    include = ["id"]
    app_id = "test"

    projects = [{"id": "project_id_123"}] * 100

    def callback(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        page = int(params.get("page", 1))
        size = int(params.get("size", 50))
        total_items = len(projects)

        # Throws an expected 404 at the last page
        start_index = (page - 1) * size
        if start_index >= len(projects):
            return httpx.Response(status_code=404)

        return httpx.Response(
            status_code=200,
            json={
                # Slice handles 1-indexed pages
                "items": projects[start_index : start_index + size],
                "total": total_items,
                "page": page,
                "size": size,
                "pages": (total_items + size - 1) // size,
            },
        )

    httpx_mock.add_callback(
        callback,
        url=re.compile(rf"{client._api_url}/v1/projects\?*"),
        method="GET",
        is_reusable=True,
    )

    result = list(
        client.projects.iterate_projects(
            creator_id=creator_id,
            include=include,
            app_id=app_id,
        )
    )
    assert len(result) == 100
    assert result == projects


def test_get_project_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test fetching a project by its ID."""
    project_id = "project_id_123"
    include = ["id"]
    mock_response = {"id": "project_id_123"}
    url = httpx.URL(url=f"{client._api_url}/v1/projects/{project_id}", params={"include": include})
    httpx_mock.add_response(
        method="GET",
        url=url,
        status_code=200,
        json=mock_response,
    )
    project = client.projects.get_project(project_id=project_id, include=include)
    assert "id" in project
    assert project["id"] == project_id


def test_get_project_missing(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test error handling when fetching a project."""
    project_id = "project_id_123"
    include = []
    mock_error = {"error": "Project not found"}
    url = httpx.URL(url=f"{client._api_url}/v1/projects/{project_id}", params={"include": include})
    httpx_mock.add_response(
        method="GET",
        url=url,
        status_code=404,
        json=mock_error,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.get_project(project_id=project_id, include=[])
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error


def test_create_project_recommendation_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project recommendation creation success."""
    project_id = "project_id_123"
    mock_response = {
        "result": {
            "created_at": "sometime in the recent past, but not now",
            "updated_at": "later from then in the near future, but not now",
            "id": "recommendation_123",
        }
    }
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects/{project_id}/recommendations",
    )
    httpx_mock.add_response(
        method="POST",
        url=url,
        status_code=200,
        json=mock_response,
    )
    recommendation = client.projects.create_project_recommendation(
        project_id=project_id,
    )
    assert recommendation == mock_response["result"]


def test_create_project_recommendation_failure(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project recommendation creation failure."""
    project_id = "project_id_123"
    mock_error = {"error": "Recommendation cannot be created"}
    url = httpx.URL(
        url=f"{client._api_url}/v1/projects/{project_id}/recommendations",
    )
    httpx_mock.add_response(
        method="POST",
        url=url,
        status_code=404,
        json=mock_error,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.create_project_recommendation(
            project_id=project_id,
        )
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error


def test_get_project_recommendation_success(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project recommendation fetching success."""
    project_id = "project_id_123"
    recommendation_id = "recommendation_123"
    mock_response = {
        "result": {
            "created_at": "sometime in the recent past, but not now",
            "updated_at": "later from then in the near future, but not now",
            "id": recommendation_id,
        }
    }
    url = httpx.URL(
        url=(f"{client._api_url}/v1/projects/{project_id}/recommendations/{recommendation_id}")
    )
    httpx_mock.add_response(
        method="GET",
        url=url,
        status_code=200,
        json=mock_response,
    )
    recommendation = client.projects.get_project_recommendation(
        recommendation_id=recommendation_id,
        project_id=project_id,
    )
    assert recommendation == mock_response["result"]


def test_get_project_recommendation_failure(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
) -> None:
    """Test project recommendation fetching failure."""
    project_id = "project_id_123"
    recommendation_id = "recommendation_123"
    mock_error = {"error": "Recommendation cannot be retrieved"}
    url = httpx.URL(
        url=(f"{client._api_url}/v1/projects/{project_id}/recommendations/{recommendation_id}")
    )
    httpx_mock.add_response(
        method="GET",
        url=url,
        status_code=404,
        json=mock_error,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client.projects.get_project_recommendation(
            recommendation_id=recommendation_id,
            project_id=project_id,
        )
    assert exc_info.value.response.status_code == 404
    assert exc_info.value.response.json() == mock_error
