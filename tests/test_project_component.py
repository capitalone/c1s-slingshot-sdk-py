import math
import random
import re
from typing import Any, cast

import httpx
import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient
from slingshot.types import (
    Page,
    ProjectCreatorSchema,
    ProjectMetricsSchema,
    ProjectSchema,
    ProjectSettingsSchema,
    RecommendationDetailsSchema,
)

# --- Test Payloads ---
creator_jane: ProjectCreatorSchema = {
    "userId": "user_1a2b",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@example.com",
    "auth0Id": "auth0|64a4b1...",
    "tenantId": "t_123",
    "isTenantAdmin": True,
    "isActive": True,
    "isRegistered": True,
    "createdAt": "2024-01-15T14:20:00Z",
    "updatedAt": "2025-06-10T11:05:00Z",
}
creator_john: ProjectCreatorSchema = {
    "userId": "user_3c4d",
    "firstName": "John",
    "lastName": "Smith",
    "email": "john.smith@example.com",
    "auth0Id": None,
    "tenantId": "t_123",
    "isTenantAdmin": False,
    "isActive": True,
    "isRegistered": True,
    "createdAt": "2024-03-22T18:00:00Z",
    "updatedAt": "2025-07-01T09:30:00Z",
}
creator_admin: ProjectCreatorSchema = {
    "userId": "user_5e6f",
    "firstName": "System",
    "lastName": "Admin",
    "email": "admin@example.com",
    "auth0Id": "auth0|88c8d2...",
    "tenantId": "t_123",
    "isTenantAdmin": False,
    "isActive": True,
    "isRegistered": False,
    "createdAt": "2023-11-01T00:00:00Z",
    "updatedAt": "2023-11-01T00:00:00Z",
}

settings_alpha: ProjectSettingsSchema = {
    "sla_minutes": 60,
    "auto_apply_recs": True,
    "fix_scaling_type": False,
    "optimize_instance_size": True,
}
settings_beta: ProjectSettingsSchema = {
    "sla_minutes": None,
    "auto_apply_recs": False,
    "fix_scaling_type": None,
    "optimize_instance_size": True,
}
settings_delta: ProjectSettingsSchema = {
    "sla_minutes": 240,
    "auto_apply_recs": False,
    "fix_scaling_type": False,
    "optimize_instance_size": False,
}
settings_epsilon: ProjectSettingsSchema = {
    "sla_minutes": None,
    "auto_apply_recs": True,
    "fix_scaling_type": True,
    "optimize_instance_size": None,
}

metrics_alpha: ProjectMetricsSchema = {
    "job_success_rate_percent": 98,
    "sla_met_percent": 99,
    "estimated_savings": 1500,
}
metrics_delta: ProjectMetricsSchema = {
    "job_success_rate_percent": 100,
    "sla_met_percent": 100,
    "estimated_savings": 450,
}
metrics_epsilon: ProjectMetricsSchema = {
    "job_success_rate_percent": 99,
    "sla_met_percent": 95,
    "estimated_savings": 200,
}

mock_projects: list[ProjectSchema] = [
    {
        "id": "proj_a1b2c3d4",
        "name": "Alpha ETL Pipeline",
        "created_at": "2025-07-21T10:30:00Z",
        "updated_at": "2025-07-21T11:00:00Z",
        "app_id": "app-alpha-etl",
        "cluster_path": "/clusters/alpha",
        "job_id": "job-112233",
        "workspace_id": "ws-prod-1",
        "creator_id": "user_1a2b",
        "product_code": "P-STREAM",
        "product_name": "DataStream Pro",
        "phase": "ACTIVE",
        "description": "Daily customer event data processing.",
        "settings": settings_alpha,
        "metrics": metrics_alpha,
        "creator": creator_jane,
    },
    {
        "id": "proj_b2c3d4e5",
        "name": "Beta Analytics Dashboard",
        "created_at": "2025-07-20T09:00:00Z",
        "updated_at": "2025-07-20T09:05:00Z",
        "app_id": None,
        "cluster_path": None,
        "job_id": None,
        "workspace_id": "ws-analytics-1",
        "creator_id": "user_3c4d",
        "product_code": "P-ANALYTICS",
        "product_name": "Insight Suite",
        "phase": "PENDING",
        "description": None,
        "settings": None,
        "metrics": None,
        "creator": creator_john,
    },
    {
        "id": "proj_c3d4e5f6",
        "name": "Gamma Data Warehouse Ingest",
        "created_at": "2025-06-15T14:00:00Z",
        "updated_at": "2025-07-18T11:20:00Z",
        "app_id": None,
        "cluster_path": None,
        "job_id": None,
        "workspace_id": None,
        "creator_id": None,
        "product_code": "P-DWH",
        "product_name": "Data Warehouse",
        "phase": "ACTIVE",
        "description": None,
        "settings": None,
        "metrics": None,
        "creator": None,
    },
    {
        "id": "proj_d4e5f6a7",
        "name": "Delta ML Model Training",
        "created_at": "2025-01-10T18:45:00Z",
        "updated_at": "2025-03-05T19:00:00Z",
        "app_id": "app-delta-ml",
        "cluster_path": "/clusters/ml-gpu",
        "job_id": "job-778899",
        "workspace_id": None,
        "creator_id": "user_1a2b",
        "product_code": "P-AI",
        "product_name": "AI/ML Platform",
        "phase": "ARCHIVED",
        "description": "Sentiment analysis model v2.",
        "settings": None,
        "metrics": metrics_alpha,
        "creator": creator_jane,
    },
    {
        "id": "proj_e5f6a7b8",
        "name": "Epsilon Alerting Service",
        "created_at": "2025-05-01T12:00:00Z",
        "updated_at": "2025-07-21T08:15:30Z",
        "app_id": None,
        "cluster_path": "/clusters/epsilon-alerts",
        "job_id": None,
        "workspace_id": "ws-epsilon-prod",
        "creator_id": "user_3c4d",
        "product_code": "P-ALERT",
        "product_name": "Proactive Alerting",
        "phase": "MAINTENANCE",
        "description": "Real-time anomaly detection.",
        "settings": settings_alpha,
        "metrics": None,
        "creator": creator_john,
    },
]


@pytest.fixture
def client() -> SlingshotClient:
    """Provides a SlingshotClient instance for tests."""
    return SlingshotClient(api_key="test_key", api_url="https://api.test.com")


@pytest.mark.parametrize(
    "call_count",
    [
        (20),
        (40),
        (50),
    ],
)
def test_call_get_project_n_times(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
    call_count: int,
) -> None:
    """Tests that `get_project` returns the correct data when called multiple times.

    This test simulates `n` consecutive API calls, each with a unique,
    randomly selected mock payload. It asserts that the result of each call
    matches its corresponding mock data and that the total number of API
    requests is correct.
    """
    randomized_payload_set = random.choices(mock_projects, k=call_count)

    for i in range(call_count):
        project_id = f"project_{i}"

        httpx_mock.add_response(
            method="GET",
            url=re.compile(rf"{client._api_url}/v1/projects/\w+"),
            json=randomized_payload_set[i],
            status_code=200,
        )

        result = client.projects.get_project(
            project_id=project_id,
            include=["id", "name"],
        )

        assert result == randomized_payload_set[i]
    assert len(httpx_mock.get_requests()) == call_count


mock_project_response: ProjectSchema = {
    "id": "proj_a1b2c3d4",
    "name": "Test Project",
    "created_at": "2025-07-21T11:00:00Z",
    "updated_at": "2025-07-21T11:00:00Z",
    "app_id": "app-test",
    "cluster_path": "/clusters/test",
    "job_id": "job-test",
    "workspace_id": "ws-test",
    "creator_id": "user_test",
    "product_code": "P-TEST",
    "product_name": "Test Product",
    "phase": "ACTIVE",
    "description": "A test project.",
    "settings": None,
    "metrics": None,
    "creator": None,
}


@pytest.mark.parametrize(
    "create_args, expected_payload",
    [
        (
            {"name": "Simple Project", "product_code": "P-SIMPLE"},
            {"name": "Simple Project", "product_code": "P-SIMPLE"},
        ),
        (
            {
                "name": "Complex Project",
                "product_code": "P-COMPLEX",
                "app_id": "app_123",
                "description": "A test.",
            },
            {
                "name": "Complex Project",
                "product_code": "P-COMPLEX",
                "app_id": "app_123",
                "description": "A test.",
            },
        ),
        (
            {
                "name": "Project With Settings",
                "product_code": "P-SETTINGS",
                "settings": {"sla_minutes": 120},
            },
            {
                "name": "Project With Settings",
                "product_code": "P-SETTINGS",
                "settings": {"sla_minutes": 120},
            },
        ),
    ],
)
def test_create_project(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
    create_args: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    """Tests that the create method sends the correct JSON payload."""
    httpx_mock.add_response(
        method="POST",
        url=f"{client._api_url}/v1/projects",
        json={"result": mock_project_response},
        status_code=201,
    )

    result = client.projects.create(**create_args)

    assert result == mock_project_response
    # Verify the payload sent to the API
    request = httpx_mock.get_requests()[0]
    assert (
        request.read().decode() == httpx.Request("POST", "/", json=expected_payload).read().decode()
    )


@pytest.mark.parametrize(
    "update_args, expected_payload",
    [
        # Test case 1: Update only the name
        ({"name": "New Project Name"}, {"name": "New Project Name"}),
        # Test case 2: Update settings and description
        (
            {"description": "New description.", "settings": {"auto_apply_recs": False}},
            {"description": "New description.", "settings": {"auto_apply_recs": False}},
        ),
    ],
)
def test_update_project(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
    update_args: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    """Tests that the update method sends the correct partial JSON payload."""
    project_id = "proj_to_update"
    httpx_mock.add_response(
        method="PUT",
        url=f"{client._api_url}/v1/projects/{project_id}",
        json={"result": mock_project_response},
        status_code=200,
    )

    result = client.projects.update(project_id=project_id, **update_args)

    assert result == mock_project_response
    request = httpx_mock.get_requests()[0]
    assert (
        request.read().decode() == httpx.Request("PUT", "/", json=expected_payload).read().decode()
    )


@pytest.mark.parametrize(
    "total_items, page_size",
    [
        (5, 50),  # Less than one page
        (100, 50),  # Exactly two pages
        (101, 50),  # A partial final page
    ],
)
def test_iterate_projects(
    httpx_mock: HTTPXMock, client: SlingshotClient, total_items: int, page_size: int
) -> None:
    """Tests that iterate_projects yields all items across multiple pages."""
    # Create a full dataset for the mock API to serve
    full_dataset: list[ProjectSchema] = [
        {
            "id": f"proj_{i}",
            "name": f"Test Project {i}",
            "created_at": "2025-07-21T11:30:00Z",
            "updated_at": "2025-07-21T11:30:00Z",
            "app_id": None,
            "cluster_path": None,
            "job_id": None,
            "workspace_id": None,
            "creator_id": None,
            "product_code": "P-TEST",
            "product_name": "Test Product",
            "description": None,
            "settings": None,
            "metrics": None,
            "creator": None,
            "phase": "ACTIVE",
        }
        for i in range(total_items)
    ]

    def paginated_callback(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        page = int(params.get("page", 1))
        size = int(params.get("size", 50))

        start = (page - 1) * size
        end = start + size
        items_slice = full_dataset[start:end]

        response_json: Page[ProjectSchema] = {
            "page": page,
            "pages": math.ceil(total_items / size),
            "items": cast(list[ProjectSchema], items_slice),
        }
        return httpx.Response(status_code=200, json=response_json)

    httpx_mock.add_callback(paginated_callback, method="GET", is_reusable=True)

    result = list(client.projects.iterate_projects(include=["id"], size=page_size))

    assert len(result) == total_items
    assert result == full_dataset


def test_create_project_recommendation(httpx_mock: HTTPXMock, client: SlingshotClient) -> None:
    """Tests that create_project_recommendation POSTs to the correct endpoint."""
    project_id = "proj_123"
    expected_response: RecommendationDetailsSchema = {
        "created_at": "2025-07-21T11:28:00Z",
        "updated_at": "2025-07-21T11:28:00Z",
        "id": "rec_abc",
        "state": "PENDING",
        "error": None,
        "recommendation": None,
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{client._api_url}/v1/projects/{project_id}/recommendations",
        json={"result": expected_response},
        status_code=202,
    )

    result = client.projects.create_project_recommendation(project_id=project_id)
    assert result == expected_response


def test_get_project_recommendation(httpx_mock: HTTPXMock, client: SlingshotClient) -> None:
    """Tests that get_project_recommendation GETs from the correct endpoint."""
    project_id = "proj_123"
    recommendation_id = "rec_abc"
    expected_response: RecommendationDetailsSchema = {
        "id": "rec_abc",
        "state": "COMPLETED",
        "created_at": "2025-07-21T11:28:00Z",
        "updated_at": "2025-07-21T11:29:00Z",
        "error": None,
        "recommendation": None,
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/v1/projects/{project_id}/recommendations/{recommendation_id}",
        json={"result": expected_response},
        status_code=200,
    )

    result = client.projects.get_project_recommendation(
        project_id=project_id, recommendation_id=recommendation_id
    )
    assert result == expected_response
