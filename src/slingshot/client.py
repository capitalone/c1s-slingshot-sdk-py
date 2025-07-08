import logging
import os
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Optional

import httpx

from slingshot.types import JSON_TYPE

from .__version__ import __version__ as __vers

if TYPE_CHECKING:
    from .api.projects import ProjectAPI

USER_AGENT = f"Slingshot Library/{__vers} (c1s-slingshot-sdk-py)"
DEFAULT_API_URL = "https://slingshot.capitalone.com/api"

logger = logging.getLogger(__name__)


class SlingshotClient:
    """SlingshotClient is a client for interacting with the Slingshot API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = DEFAULT_API_URL,
    ):
        """Initialize the Slingshot client.

        Args:
            api_key (str): The API key for authentication. If not provided, it will look
                for the environment variable SLINGSHOT_API_KEY.
            api_url (str): The base URL for the Slingshot API. Defaults to DEFAULT
                API_URL.

        Raises:
            ValueError: If the API key is not provided and not found in the environment.

        Example:
            >>> from slingshot.client import SlingshotClient
            >>> client = SlingshotClient(api_key="your_api_key")

        """
        self._api_url = api_url
        if not api_key:
            api_key = os.getenv("SLINGSHOT_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided either as a parameter or in the environment variable SLINGSHOT_API_KEY"
                )
        self._api_key = api_key

    def _api_request(
        self, method: Literal["GET", "POST", "PUT", "DELETE"], endpoint: str
    ) -> JSON_TYPE:
        """Make an API request to the Slingshot API."""
        headers = {
            "Auth": self._api_key,
            "User-Agent": USER_AGENT,
        }
        url = f"{self._api_url}{endpoint}"
        response = httpx.request(method=method, url=url, headers=headers)
        response.raise_for_status()
        return response.json()

    @cached_property
    def projects(self) -> "ProjectAPI":
        """Get the projects API client."""
        from .api.projects import ProjectAPI

        return ProjectAPI(self)
