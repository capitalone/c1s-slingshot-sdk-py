import logging
import os
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Optional

import backoff
import httpx

from slingshot.types import JSON_TYPE, UNSET, QueryParams

from .__vers import __version__

if TYPE_CHECKING:
    from .api.projects import ProjectAPI


USER_AGENT = f"Slingshot Library/{__version__} (c1s-slingshot-sdk-py)"
DEFAULT_API_URL = "https://slingshot.capitalone.com/prod/api/gradient"

logger = logging.getLogger(__name__)


def _httpx_giveup_codes(e: Exception) -> bool:
    """Determine whether to give up on retrying based on the HTTP status code."""
    if not isinstance(e, httpx.HTTPStatusError):
        return False
    if e.response is None:
        return False
    if e.request.method in {"GET", "DELETE", "HEAD", "OPTIONS"}:
        return e.response.status_code not in {500, 503, 502, 504, 429}
    if e.request.method in {"POST", "PUT"}:
        return e.response.status_code not in {429}
    return False


def _remove_unset_keys(obj):
    """Recursively removes items or key-value pairs that are UNSET."""
    if isinstance(obj, dict):
        # Create a new dict, skipping keys where the value is UNSET
        return {k: _remove_unset_keys(v) for k, v in obj.items() if v is not UNSET}
    elif isinstance(obj, list):
        # Create a new list, filtering out any UNSET items
        return [_remove_unset_keys(i) for i in obj if i is not UNSET]
    else:
        return obj


class SlingshotClient:
    """SlingshotClient is a client for interacting with the Slingshot API.

    Get an API key from: https://slingshot.capitalone.com/configurations/api-keys
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        """Initialize the Slingshot client.

        Args:
            api_key (str): The API key for authentication. If not provided, it will look
                for the environment variable SLINGSHOT_API_KEY.
            api_url (str): The base URL for the Slingshot API. If not provided, it will look
                for the environment variable SLINGSHOT_API_URL, if not set, it will default
                to "https://slingshot.capitalone.com/prod/api/gradient".

        Raises:
            ValueError: If the API key is not provided and not found in the environment.

        Example:
            >>> from slingshot.client import SlingshotClient
            >>> # Or:
            >>> # from slingshot import SlingshotClient
            >>> client = SlingshotClient(api_key="your_api_key")

        """
        if not api_key:
            api_key = os.getenv("SLINGSHOT_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided either as a parameter or in the environment variable SLINGSHOT_API_KEY"
                )
        self._api_key = api_key

        self._api_url = api_url or os.getenv("SLINGSHOT_API_URL") or DEFAULT_API_URL

    def __repr__(self):
        """Return a string representation of the SlingshotClient."""
        return f'SlingshotClient(api_url="{self._api_url}", api_key="***")'

    @backoff.on_exception(
        backoff.expo,
        httpx.HTTPStatusError,
        logger=logger,
        max_tries=5,
        giveup=_httpx_giveup_codes,
    )
    def _api_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
        endpoint: str,
        json: Optional[JSON_TYPE] = None,
        params: Optional[QueryParams] = None,
    ) -> Optional[JSON_TYPE]:
        """Make an API request to the Slingshot API."""
        headers = {
            "Auth": self._api_key,
            "User-Agent": USER_AGENT,
        }
        url = f"{self._api_url}{endpoint}"
        # Removes all the UNSET values from the json

        json = _remove_unset_keys(json)
        response = httpx.request(method=method, url=url, headers=headers, json=json, params=params)
        response.raise_for_status()
        if (
            response.headers
            and response.headers.get("content-type", "") == "application/json"
            and response.text  # Some routes can return content-type json without data, usually with 204 code.
        ):
            return response.json()
        elif response.status_code == 204:
            return None
        else:
            raise RuntimeError(
                "Unhandled API response: response was not of type 'application/json'"
            )

    @cached_property
    def projects(self) -> "ProjectAPI":
        """Get the projects API client."""
        from .api.projects import ProjectAPI

        return ProjectAPI(self)
