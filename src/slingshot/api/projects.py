from typing import cast

import httpx

from slingshot.client import SlingshotClient
from slingshot.exceptions import ResourceNotFoundError
from slingshot.types import ProjectSchema


class ProjectAPI:
    """API for managing projects in Slingshot."""

    def __init__(self, client: SlingshotClient):
        """Initialize the ProjectAPI."""
        self.client = client

    def get_project(
        self,
        project_id: str,
    ) -> ProjectSchema:
        """Fetch a project by its ID.

        Args:
            project_id (str): The ID of the project to fetch.

        Returns:
            ProjectSchema: The project details.

        Raises:
            ResourceNotFoundError: If the project with the given ID does not exist.

        """
        try:
            response = self.client._api_request(method="GET", endpoint=f"/v1/projects/{project_id}")
            return cast(ProjectSchema, response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ResourceNotFoundError(resource="Project", identifier=project_id) from None
            raise
