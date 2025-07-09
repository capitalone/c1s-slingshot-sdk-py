from typing import Literal

import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient


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
