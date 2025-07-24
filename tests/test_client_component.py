import httpx
import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient


def test_api_request_with_invalid_key(httpx_mock: HTTPXMock) -> None:
    """Tests that an HTTPStatusError is raised for an invalid API key (401 response)."""
    httpx_mock.add_response(
        status_code=401,
        json={"detail": "Invalid authentication credentials"},
    )
    client = SlingshotClient(api_key="invalid_key")

    with pytest.raises(httpx.HTTPStatusError) as e:
        client._api_request("GET", "/v1/some-endpoint")

    assert e.value.response.status_code == 401


def test_api_request_with_valid_key(httpx_mock: HTTPXMock) -> None:
    """Tests that a valid API key is correctly sent in the 'Auth' header."""
    client = SlingshotClient(api_key="a_valid_key")
    expected_response = {"data": "success"}

    httpx_mock.add_response(status_code=200, json=expected_response)

    response_data = client._api_request("GET", "/v1/any-endpoint")

    assert response_data == expected_response

    request = httpx_mock.get_requests()[0]
    assert request.headers["Auth"] == "a_valid_key"
