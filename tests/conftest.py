import pytest
from pytest_httpx import HTTPXMock

from slingshot.client import SlingshotClient


@pytest.fixture(scope="session")
def api_key() -> str:
    """Fixture to provide the API key for SlingshotClient."""
    # Use a test API key for testing purposes
    return "TENANTID~123~ad24a52646945572ad43654c7a0152a3b3fd55cf7cd1aea3a8e189692799dfc3"


@pytest.fixture(scope="function")
def client(api_key: str, httpx_mock: HTTPXMock) -> SlingshotClient:
    """Fixture to create a SlingshotClient instance for testing."""
    # Use a test API key and URL for testing purposes
    api_url = "https://test.slingshot.capitalone.com/prod/api/gradient"

    return SlingshotClient(api_key=api_key, api_url=api_url)
