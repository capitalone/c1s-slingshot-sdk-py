import pytest

from slingshot.client import SlingshotClient


@pytest.fixture(scope="session")
def client() -> SlingshotClient:
    """Fixture to create a SlingshotClient instance for testing."""
    # Use a test API key and URL for testing purposes
    api_key = "test_api_key"
    api_url = "https://test.slingshot.capitalone.com/api"

    return SlingshotClient(api_key=api_key, api_url=api_url)
