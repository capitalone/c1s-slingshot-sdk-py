import os
from importlib.metadata import version as get_version
from typing import Literal

import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient

__version__ = get_version("c1s-slingshot-sdk-py")


@pytest.mark.parametrize(
    "status_code",
    [500, 502, 503, 504, 429],
)
@pytest.mark.parametrize("method", ["GET", "HEAD", "DELETE"])
def test_retries_get_on_status_code(
    httpx_mock: HTTPXMock,
    client: SlingshotClient,
    status_code: int,
    method: Literal["GET", "HEAD", "DELETE"],
) -> None:
    """Test retries on acceptable status code."""
    httpx_mock.add_response(
        method=method,
        url=f"{client._api_url}/TEST",
        status_code=status_code,
    )
    httpx_mock.add_response(
        method=method,
        url=f"{client._api_url}/TEST",
        status_code=200,
        json={"success": True},
    )
    result = client._api_request(method=method, endpoint="/TEST")
    assert result == {"success": True}


@pytest.mark.parametrize(
    "status_code",
    [429],
)
@pytest.mark.parametrize(
    "method",
    ["POST", "PUT"],
)
def test_post_put_retries_on_status_code(
    httpx_mock: HTTPXMock, client: SlingshotClient, status_code: int, method: Literal["POST", "PUT"]
) -> None:
    """Test retries on acceptable status code for POST and PUT."""
    httpx_mock.add_response(
        method=method,
        url=f"{client._api_url}/TEST",
        status_code=status_code,
    )
    httpx_mock.add_response(
        method=method,
        url=f"{client._api_url}/TEST",
        status_code=200,
        json={"success": True},
    )
    result = client._api_request(method=method, endpoint="/TEST")
    assert result == {"success": True}


def test_api_key_from_env(client: SlingshotClient, httpx_mock: HTTPXMock) -> None:
    """Test that the API key can be set from environment variable."""
    os.environ["SLINGSHOT_API_KEY"] = "test_api_key"
    client_with_env_key = SlingshotClient()
    httpx_mock.add_response(
        method="GET",
        url=f"{client_with_env_key._api_url}/v1/projects/test_project",
        status_code=200,
        json={"id": "test_project"},
        match_headers={
            "Auth": "test_api_key",
            "User-Agent": f"Slingshot Library/{__version__} (c1s-slingshot-sdk-py)",
        },
    )
    client_with_env_key.projects.get_project(
        project_id="test_project",
        include=[],
    )
    del os.environ["SLINGSHOT_API_KEY"]  # no leaks


def test_no_api_key_raises_error() -> None:
    """Test that an error is raised if no API key is provided."""
    with pytest.raises(
        ValueError,
        match="API key must be provided either as a parameter or in the environment variable SLINGSHOT_API_KEY",
    ):
        SlingshotClient(api_key=None)


@pytest.mark.parametrize("status_code", [200])
def test_nonserializable_response(
    httpx_mock: HTTPXMock, client: SlingshotClient, status_code: int
) -> None:
    """Test retries on acceptable status code for POST and PUT."""
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/TEST",
        status_code=status_code,
    )

    result = client._api_request(method="GET", endpoint="/TEST")
    assert result == "200"
