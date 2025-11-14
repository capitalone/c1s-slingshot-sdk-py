from collections.abc import Iterator, Mapping
from typing import Any, Optional, cast

import httpx

from slingshot.client import SlingshotClient
from slingshot.types import (
    JSON_TYPE,
    UNSET,
    AssignSettingsSchema,
    Page,
    ProjectSchema,
    QueryParams,
    RecommendationDetailsSchema,
)

MAX_PAGES = 1000


def _dict_set_if_not_unset(
    source: Mapping[str, Any], destination: dict[str, Any], key: str
) -> None:
    """Helper function for dicts that sets if the assigning value is not unset.

    Checks for a key in a source mapping and, if its value is not UNSET,
    adds the key and value to the destination dict.

    Args:
        source (Mapping[str, Any]): The mapping to read from.
        destination (dict[str, Any]): The dict to write to.
        key (str): The key to transfer.
    """
    value = source.get(key, UNSET)
    if value is not UNSET:
        destination[key] = value


class ProjectAPI:
    """API for managing projects in Slingshot."""

    def __init__(self, client: SlingshotClient):
        """Initialize the ProjectAPI."""
        self.client = client

    def create(
        self,
        name: str,
        workspaceId: str,
        app_id: Optional[str] = UNSET,
        cluster_path: Optional[str] = UNSET,
        job_id: Optional[str] = UNSET,
        subscriptionId: Optional[str] = UNSET,
        description: Optional[str] = UNSET,
        cluster_log_url: Optional[str] = UNSET,
        settings: Optional[AssignSettingsSchema] = UNSET,
    ) -> ProjectSchema:
        """Create a new project.

        Note: See API documentation for default values of parameters.

        Args:
            name (str): The name of the project.
            workspaceId (str): The workspace ID.
            settings (ProjectAdditionalSettingsSchema): A object for
            additional settings.
            app_id (Optional[str], optional): The application ID.
            cluster_path (Optional[str], optional): The path to the cluster.
            job_id (Optional[str], optional): The job ID.
            subscriptionId (Optional[str], optional): The subscription ID.
            description (Optional[str], optional): A description for the project.
            cluster_log_url (Optional[str], optional): The URL for cluster logs.
            settings (AssignSettingsSchema, optional): An object that specifies options.
                sla_minutes (Optional[int], optional): Option to set the SLA minutes.
                fix_scaling_type (Optional[bool], optional): Option to fix the scaling type.
                auto_apply_recs (Optional[bool], optional): Option to auto apply recommendations.
                optimize_instance_size (Optional[bool], optional): Option to optimize the instance size.

        Returns:
            ProjectSchema: The details of the newly created project.

        """
        json: JSON_TYPE = {"name": name, "workspaceId": workspaceId}

        if app_id is not UNSET:
            json["app_id"] = app_id
        if cluster_path is not UNSET:
            json["cluster_path"] = cluster_path
        if job_id is not UNSET:
            json["job_id"] = job_id
        if subscriptionId is not UNSET:
            json["subscriptionId"] = subscriptionId
        if description is not UNSET:
            json["description"] = description
        if cluster_log_url is not UNSET:
            json["cluster_log_url"] = cluster_log_url

        if settings is not UNSET and settings is not None:
            json["settings"] = {}
            _dict_set_if_not_unset(settings, json["settings"], "sla_minutes")
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "fix_scaling_type",
            )
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "auto_apply_recs",
            )
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "optimize_instance_size",
            )
        elif settings is None:
            json["settings"] = None

        response = cast(
            dict[str, Any],
            self.client._api_request(
                method="POST",
                endpoint="/v1/projects",
                json=json,
            ),
        )

        return cast(
            ProjectSchema,
            response.get("result"),
        )

    def update(
        self,
        project_id: str,
        name: Optional[str] = UNSET,
        cluster_path: Optional[str] = UNSET,
        job_id: Optional[str] = UNSET,
        workspaceId: Optional[str] = UNSET,
        subscriptionId: Optional[str] = UNSET,
        description: Optional[str] = UNSET,
        cluster_log_url: Optional[str] = UNSET,
        settings: Optional[AssignSettingsSchema] = UNSET,
    ) -> ProjectSchema:
        """Update an existing project's attributes.

        Note: See API documentation for default values of parameters.

        Args:
            project_id (str): The ID of the project to update.
            name (Optional[str], optional): The new name for the project.
            cluster_path (Optional[str], optional): The new path to the cluster.
            job_id (Optional[str], optional): The new job ID.
            workspaceId (Optional[str], optional): The new workspace ID.
            subscriptionId (Optional[str], optional): The new subscription ID.
            description (Optional[str], optional): The new description for the
            project.
            cluster_log_url (Optional[str], optional): The new URL for cluster logs.
            settings (AssignSettingsSchema, optional): An object that specifies options.
                sla_minutes (Optional[int], optional): Option to set the SLA minutes.
                fix_scaling_type (Optional[bool], optional): Option to fix the scaling type.
                auto_apply_recs (Optional[bool], optional): Option to auto apply recommendations.
                optimize_instance_size (Optional[bool], optional): Option to optimize the instance size.

        Returns:
            ProjectSchema: The details of the updated project.

        """
        json: JSON_TYPE = {}

        if name is not UNSET:
            json["name"] = name
        if cluster_path is not UNSET:
            json["cluster_path"] = cluster_path
        if job_id is not UNSET:
            json["job_id"] = job_id
        if workspaceId is not UNSET:
            json["workspaceId"] = workspaceId
        if subscriptionId is not UNSET:
            json["subscriptionId"] = subscriptionId
        if description is not UNSET:
            json["description"] = description
        if cluster_log_url is not UNSET:
            json["cluster_log_url"] = cluster_log_url

        if settings is not UNSET and settings is not None:
            json["settings"] = {}
            _dict_set_if_not_unset(settings, json["settings"], "sla_minutes")
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "fix_scaling_type",
            )
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "auto_apply_recs",
            )
            _dict_set_if_not_unset(
                settings,
                json["settings"],
                "optimize_instance_size",
            )
        elif settings is None:
            json["settings"] = None

        response = cast(
            dict[str, Any],
            self.client._api_request(
                method="PUT",
                endpoint=f"/v1/projects/{project_id}",
                json=json,
            ),
        )

        return cast(
            ProjectSchema,
            response.get("result"),
        )

    def get_projects(
        self,
        include: list[str],
        creator_id: Optional[str] = None,
        app_id: Optional[str] = None,
        job_id: Optional[str] = None,
        page: int = 1,
        size: int = 50,
    ) -> Page[ProjectSchema]:
        """Retrieve a paginated list of projects based on filter criteria.

        Args:
            include (list[str]): Specifies related resources to include the
            response.
            creator_id (Optional[str], optional): The ID of the creator to
            filter projects by. Defaults to None.
            app_id (Optional[str], optional): The application ID to filter
            projects by. Defaults to None.
            job_id (Optional[str], optional): The job ID to filter projects by.
            Defaults to None.
            page (int, optional): The page number to retrieve. Defaults to 1.
            size (int, optional): The number of projects to retrieve per page.
            Defaults to 50.

        Returns:
            Page[ProjectSchema]: A list of project details for the requested
            page.

        """
        params: QueryParams = {
            "include": include,
            "page": cast(str, page),
            "size": cast(str, size),
        }

        if creator_id is not None:
            params["creator_id"] = creator_id
        if app_id is not None:
            params["app_id"] = app_id
        if job_id is not None:
            params["job_id"] = job_id

        response: Page[ProjectSchema] = cast(
            Page[ProjectSchema],
            self.client._api_request(method="GET", endpoint="/v1/projects", params=params),
        )

        return response

    def iterate_projects(
        self,
        include: list[str],
        creator_id: Optional[str] = None,
        app_id: Optional[str] = None,
        job_id: Optional[str] = None,
        size: int = 50,
        max_pages: int = MAX_PAGES,
    ) -> Iterator[ProjectSchema]:
        """A memory-efficient generator that fetches all projects page by page.

        Args:
            include (list[str]): Specifies related resources to include the
            response.
            creator_id (Optional[str], optional): The ID of the creator to
            filter projects by. Defaults to None.
            app_id (Optional[str], optional): The application ID to filter
            projects by. Defaults to None.
            job_id (Optional[str], optional): The job ID to filter projects by.
            Defaults to None.
            size (int, optional): The number of projects to retrieve per page.
            Defaults to 50.
            max_pages (int, optional): The maximum number of pages allowed to
            traverse. Defaults to 1000.

        Yields:
            Iterator[ProjectSchema]: A project object, one at a time.

        """
        page = 1
        while True:
            try:
                response_page: Page[ProjectSchema] = self.get_projects(
                    include=include,
                    creator_id=creator_id,
                    app_id=app_id,
                    job_id=job_id,
                    page=page,
                    size=size,
                )

                page_number = response_page["page"]
                projects: list[ProjectSchema] = response_page["items"]
                yield from projects
                if page_number >= response_page["pages"] or page_number >= max_pages:
                    break
                page += 1

            except httpx.HTTPStatusError:
                break

    def get_project(self, project_id: str, include: list[str]) -> ProjectSchema:
        """Fetch a project by its ID.

        Args:
            project_id (str): The ID of the project to fetch.
            include (list[str]): Specifies related resources to include the
            response.

        Returns:
            ProjectSchema: The project details.

        """
        params: QueryParams = {"include": include}
        response = self.client._api_request(
            method="GET", endpoint=f"/v1/projects/{project_id}", params=params
        )
        return cast(ProjectSchema, response)

    def create_project_recommendation(self, project_id: str) -> RecommendationDetailsSchema:
        """Create a new recommendation for a given project.

        Args:
            project_id (str): The ID of the project to create a recommendation
            for.

        Returns:
            RecommendationDetailsSchema: The recommendation creation status
            object.

        """
        response = cast(
            dict[str, Any],
            self.client._api_request(
                method="POST",
                endpoint=f"/v1/projects/{project_id}/recommendations",
            ),
        )

        return cast(
            RecommendationDetailsSchema,
            response.get("result"),
        )

    def get_project_recommendation(
        self,
        recommendation_id: str,
        project_id: str,
    ) -> RecommendationDetailsSchema:
        """Fetch a specific recommendation for a project.

        Args:
            recommendation_id (str): The ID of the recommendation to fetch.
            project_id (str): The ID of the project that the recommendation
            belongs to.

        Returns:
            RecommendationDetailsSchema: The details of the specific
            recommendation.

        """
        response = cast(
            dict[str, Any],
            self.client._api_request(
                method="GET",
                endpoint=f"/v1/projects/{project_id}/recommendations/{recommendation_id}",
            ),
        )

        return cast(
            RecommendationDetailsSchema,
            response.get("result"),
        )

    def reset_project(self, project_id: str) -> None:
        """Reset a project by its ID, removing all previous submission data.

        Args:
            project_id (str): The ID of the project to reset.

        Returns:
            None
        """
        self.client._api_request(method="POST", endpoint=f"/v1/projects/{project_id}")
