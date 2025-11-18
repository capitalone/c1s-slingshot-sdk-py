from importlib.metadata import version as get_version
from typing import Literal

import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient

__version__ = get_version("c1s-slingshot-sdk-py")

from src.slingshot.client import DEFAULT_API_URL


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


@pytest.fixture
def set_SLINGSHOT_API_KEY_env_var(monkeypatch):
    """The environment variable is automatically reverted by monkeypatch after the test."""
    monkeypatch.setenv("SLINGSHOT_API_KEY", "test_api_key")
    yield


def test_api_key_from_env(
    set_SLINGSHOT_API_KEY_env_var, client: SlingshotClient, httpx_mock: HTTPXMock
) -> None:
    """Test that the API key can be set from environment variable."""
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
    client_with_env_key.projects.get_project(project_id="test_project")


def test_no_api_key_raises_error() -> None:
    """Test that an error is raised if no API key is provided."""
    with pytest.raises(
        ValueError,
        match="API key must be provided either as a parameter or in the environment variable SLINGSHOT_API_KEY",
    ):
        SlingshotClient(api_key=None)


@pytest.fixture
def set_SLINGSHOT_API_URL_env_var(monkeypatch):
    """The environment variable is automatically reverted by monkeypatch after the test."""
    monkeypatch.setenv("SLINGSHOT_API_URL", "https://api.slingshot.com")
    yield


def test_api_url_from_env(set_SLINGSHOT_API_URL_env_var, client: SlingshotClient) -> None:
    """Test that the API url can be set from environment variable."""
    client = SlingshotClient(api_key="test_api_key")
    assert client._api_url == "https://api.slingshot.com"


def test_default_api_url(client: SlingshotClient) -> None:
    """Test that the API url uses default if not passed and not in env vars."""
    client = SlingshotClient(api_key="test_api_key")
    assert client._api_url == DEFAULT_API_URL


@pytest.mark.parametrize("status_code", [200])
def test_response_non_json_content_type(
    httpx_mock: HTTPXMock, client: SlingshotClient, status_code: int
) -> None:
    """Test response coming back without json content type."""
    httpx_mock.add_response(
        method="GET",
        url=f"{client._api_url}/TEST",
        status_code=status_code,
    )

    with pytest.raises(RuntimeError) as exc_info:
        client._api_request(method="GET", endpoint="/TEST")

    assert (
        str(exc_info.value) == "Unhandled API response: response was not of type 'application/json'"
    )


@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
def test_response_204(httpx_mock: HTTPXMock, client: SlingshotClient, method: str) -> None:
    """Test response coming back for a 204 no content."""
    httpx_mock.add_response(
        method=method,
        url=f"{client._api_url}/TEST",
        status_code=204,
    )

    # pyright is not happy with method: str against str Literal methods...
    assert client._api_request(method=method, endpoint="/TEST") is None  # pyright: ignore
