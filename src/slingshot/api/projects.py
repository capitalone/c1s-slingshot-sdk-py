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
        workspace_id: str,
        description: Optional[str] = UNSET,
        app_id: Optional[str] = UNSET,
        job_id: Optional[str] = UNSET,
        cluster_path: Optional[str] = UNSET,
        settings: Optional[AssignSettingsSchema] = UNSET,
    ) -> ProjectSchema:
        """Create a new Slingshot project for optimizing a Databricks job cluster.

        Args:
            name (str): The name of the Slingshot project.
            workspace_id (str): The Databricks workspace ID where the job runs.
            description (Optional[str], optional): A description for the
                Slingshot project. Defaults to None.
            app_id (Optional[str], optional): The application ID, which must
                be unique across all active (not deleted) projects belonging
                to a Slingshot subscriber. This field can be used to search
                for a project with the :meth:`get_projects` and
                :meth:`iterate_projects` methods. The `app_id` is immutable
                once the project is created. Defaults to None.
            job_id (Optional[str], optional): The Databricks job ID that will
                be associated with this Slingshot project. Defaults to None.
            cluster_path (Optional[str], optional): The name of the Databricks
                job cluster to be optimized by this Slingshot project, prefixed
                with "job_clusters/" for a job cluster that is available to any
                task in the job; or the task name prefixed with "tasks/" for a
                task-specific cluster not available to other tasks in the job.
                For example, "job_clusters/my-cluster" or "tasks/task_1".
                **This field is required if the job has multiple compute
                clusters.** If the job has only one compute cluster, this
                field is optional. Defaults to None.

                Each Slingshot project is linked to a single compute cluster in
                Databricks. If the `cluster_path` is not provided for a job
                that has multiple compute clusters, the Slingshot project will
                not be able to retrieve information about the job runs nor
                generate recommendations for optimizing the compute cluster.

                You can find the cluster name in the Databricks UI when viewing
                the configuration for a job cluster as the "Cluster name" field,
                or using the `Databricks API <https://docs.databricks.com/api/workspace/jobs/create#job_clusters-job_cluster_key>`__,
                where it is called "job_cluster_key".

                The task name is shown in the Databricks UI as the "Task name"
                field after selecting the task in the job configuration. In
                the `Databricks API <https://docs.databricks.com/api/workspace/jobs/create#tasks-task_key>`__,
                it is called "task_key".

                With the Databricks Python SDK, you can retrieve the
                `cluster_path` using the `job_cluster_key` or `task_key` from
                the job or task settings. For example, to get the
                :class:`~databricks.sdk.service.jobs.Job` object and extract the
                `job_cluster_key` or `task_key`, you can use the following code:

                >>> from databricks.sdk import WorkspaceClient
                >>> workspace_client = WorkspaceClient()
                >>> job = workspace_client.jobs.get(job_id=1234567890)

                If the job cluster is defined for the job and potentially
                shared across tasks in the job (which is the case for jobs
                created in the Databricks UI), you can retrieve the
                `job_cluster_key` like this:

                >>> cluster_name = job.settings.job_clusters[0].job_cluster_key
                >>> print(f'cluster_path="job_clusters/{cluster_name}"')

                Or, if the job cluster definition is tied to a specific
                task rather than shared across the entire job, you can first
                check whether the task is using a shared cluster, and if not,
                use the `task_key` as the `cluster_path`. When jobs are created
                with the Databricks API or SDK, tasks can be configured to use
                a `new_cluster` that is not shared with other tasks, in which
                case the `job_cluster_key` will not be set, and you should use
                the `task_key` instead:

                >>> if (cluster_name := job.settings.tasks[0].job_cluster_key):
                >>>     print(f'cluster_path="job_clusters/{cluster_name}"')
                >>> else:
                >>>     task_name = job.settings.tasks[0].task_key
                >>>     print(f'cluster_path="tasks/{task_name}"')

                See also:

                - :class:`~databricks.sdk.service.jobs.Job`
                - :class:`~databricks.sdk.service.jobs.JobSettings`
                - :class:`~databricks.sdk.service.jobs.JobCluster`
                - :class:`~databricks.sdk.service.jobs.Task`

            settings (AssignSettingsSchema, optional): A dictionary that
                sets Slingshot project options. Defaults to None.

                - sla_minutes (Optional[int], optional): The acceptable time (in minutes) for the job to complete.
                    The SLA (Service Level Agreement) is the maximum time the
                    job should take to complete. Slingshot uses this value as
                    an expected upper bound when optimizing the job for lowest
                    cost. Defaults to None.
                - fix_scaling_type (Optional[bool], optional): Whether to maintain the autoscaling settings on the Databricks job cluster (if applicable).
                    If set to True, Slingshot will keep autoscaling (if enabled)
                    when making recommendations, but will set `min_workers` and
                    `max_workers` to the same value based on Slingshot's
                    recommendations (effectively creating a fixed-size cluster).
                    If set to False, Slingshot will convert the job cluster to
                    a fixed-size cluster with the number of workers set based
                    on Slingshot's recommendations.
                    Defaults to True.
                - auto_apply_recs (Optional[bool], optional): Automatically apply recommendations.
                    Defaults to False.
                - optimize_instance_size (Optional[bool], optional): Whether to optimize the instance size.
                   If set to True, Slingshot will attempt to optimize the
                    instance size of the worker nodes while maintaining the
                    instance type (e.g., `r5.xlarge`, `r5.2xlarge`, `r5.4xlarge`).
                    Defaults to False.

                    Note: **Slingshot always optimizes the number of worker
                    nodes**. When this option is enabled, Slingshot will
                    also optimize the worker instance size.

        Returns:
            ProjectSchema: The details of the newly created project.

        """
        # The Slingshot API expects "workspaceId" to be in camelCase, the rest
        # of the keys are in snake_case.
        json: JSON_TYPE = {"name": name, "workspaceId": workspace_id}

        if app_id is not UNSET:
            json["app_id"] = app_id
        # cluster_path is the name of a job cluster prefixed by
        # "job_clusters/" or the name of a task prefixed by "tasks/".
        if cluster_path is not UNSET:
            json["cluster_path"] = cluster_path
        if job_id is not UNSET:
            json["job_id"] = job_id
        if description is not UNSET:
            json["description"] = description

        if settings is not UNSET and settings is not None:
            json["settings"] = {}
            for key in (
                "sla_minutes",
                "fix_scaling_type",
                "auto_apply_recs",
                "optimize_instance_size",
            ):
                _dict_set_if_not_unset(settings, json["settings"], key)
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
        workspace_id: Optional[str] = UNSET,
        description: Optional[str] = UNSET,
        job_id: Optional[str] = UNSET,
        cluster_path: Optional[str] = UNSET,
        settings: Optional[AssignSettingsSchema] = UNSET,
    ) -> ProjectSchema:
        """Update the attributes of an existing Slingshot project.

        Only those attributes that are provided will be updated. Attributes
        set to `None` will overwrite the project attribute with `None`.

        Args:
            project_id (str): The ID of the Slingshot project to update.
            name (Optional[str], optional): The new name for the Slingshot
                project.
            workspace_id (Optional[str], optional): The new Databricks
                workspace ID where the job runs.

                **Note**: If you are changing the Databricks workspace
                associated with the Slingshot project, you probably also want
                to reset the project using the :meth:`reset` method. This will
                remove all previous job run data from the project, allowing
                Slingshot to re-optimize the job without the influence of
                previous runs.
            description (Optional[str], optional): The new description for the
                Slingshot project.
            job_id (Optional[str], optional): The new Databricks job ID that
                will be associated with this Slingshot project.

                **Note**: If you are changing the Databricks job associated with
                the Slingshot project, you probably also want to reset the project
                using the :meth:`reset` method. This will remove all previous
                job run data from the project, allowing Slingshot to re-optimize
                the job without the influence of previous runs.
            cluster_path (Optional[str], optional): The name of the Databricks
                job cluster to be optimized by this Slingshot project, prefixed
                with "job_clusters/" for a job cluster that is available to any
                task in the job; or the task name prefixed with "tasks/" for a
                task-specific cluster not available to other tasks in the job.
                For example, "job_clusters/my-cluster" or "tasks/task_1".
                **This field is required if the job has multiple compute
                clusters.** If the job has only one compute cluster, this
                field is optional.

                Each Slingshot project is linked to a single compute cluster in
                Databricks. If the `cluster_path` is not provided for a job
                that has multiple compute clusters, the Slingshot project will
                not be able to retrieve information about the job runs nor
                generate recommendations for optimizing the compute cluster.

                You can find the cluster name in the Databricks UI when viewing
                the configuration for a job cluster as the "Cluster name" field,
                or using the `Databricks API <https://docs.databricks.com/api/workspace/jobs/create#job_clusters-job_cluster_key>`__,
                where it is called "job_cluster_key".

                The task name is shown in the Databricks UI as the "Task name"
                field after selecting the task in the job configuration. In
                the `Databricks API <https://docs.databricks.com/api/workspace/jobs/create#tasks-task_key>`__,
                it is called "task_key".

                With the Databricks Python SDK, you can retrieve the
                `cluster_path` using the `job_cluster_key` or `task_key` from
                the job or task settings. For example, to get the
                :class:`~databricks.sdk.service.jobs.Job` object and extract the
                `job_cluster_key` or `task_key`, you can use the following code:

                >>> from databricks.sdk import WorkspaceClient
                >>> workspace_client = WorkspaceClient()
                >>> job = workspace_client.jobs.get(job_id=1234567890)

                If the job cluster is defined for the job and potentially
                shared across tasks in the job (which is the case for jobs
                created in the Databricks UI), you can retrieve the
                `job_cluster_key` like this:

                >>> cluster_name = job.settings.job_clusters[0].job_cluster_key
                >>> print(f'cluster_path="job_clusters/{cluster_name}"')

                Or, if the job cluster definition is tied to a specific
                task rather than shared across the entire job, you can first
                check whether the task is using a shared cluster, and if not,
                use the `task_key` as the `cluster_path`. When jobs are created
                with the Databricks API or SDK, tasks can be configured to use
                a `new_cluster` that is not shared with other tasks, in which
                case the `job_cluster_key` will not be set, and you should use
                the `task_key` instead:

                >>> if (cluster_name := job.settings.tasks[0].job_cluster_key):
                >>>     print(f'cluster_path="job_clusters/{cluster_name}"')
                >>> else:
                >>>     task_name = job.settings.tasks[0].task_key
                >>>     print(f'cluster_path="tasks/{task_name}"')

                See also:

                - :class:`~databricks.sdk.service.jobs.Job`
                - :class:`~databricks.sdk.service.jobs.JobSettings`
                - :class:`~databricks.sdk.service.jobs.JobCluster`
                - :class:`~databricks.sdk.service.jobs.Task`

            settings (AssignSettingsSchema, optional): A dictionary with
                updates to the options for the Slingshot project. The options are:

                - sla_minutes (Optional[int], optional): The acceptable time (in minutes) for the job to complete.
                    The SLA (Service Level Agreement) is the maximum time the
                    job should take to complete. Slingshot uses this value as
                    an expected upper bound when optimizing the job for lowest
                    cost.
                - fix_scaling_type (Optional[bool], optional): Whether to maintain the autoscaling settings on the Databricks job cluster (if applicable).
                    If set to True, Slingshot will keep autoscaling (if enabled)
                    when making recommendations, but will set `min_workers` and
                    `max_workers` to the same value based on Slingshot's
                    recommendations (effectively creating a fixed-size cluster).
                    If set to False, Slingshot will convert the job cluster to
                    a fixed-size cluster with the number of workers set based
                    on Slingshot's recommendations.
                - auto_apply_recs (Optional[bool], optional): Automatically apply recommendations.
                - optimize_instance_size (Optional[bool], optional): Whether to optimize the instance size.
                    If set to True, Slingshot will attempt to optimize the
                    instance size of the worker nodes while maintaining the
                    instance type (e.g., `r5.xlarge`, `r5.2xlarge`, `r5.4xlarge`).

                    Note: **Slingshot always optimizes the number of worker
                    nodes**. When this option is enabled, Slingshot will
                    also optimize the worker instance size.

        Returns:
            ProjectSchema: The details of the updated project.

        """
        json: JSON_TYPE = {}

        if name is not UNSET:
            json["name"] = name
        # cluster_path is the name of a job cluster prefixed by
        # "job_clusters/" or the name of a task prefixed by "tasks/".
        if cluster_path is not UNSET:
            json["cluster_path"] = cluster_path
        if job_id is not UNSET:
            json["job_id"] = job_id
        # The Slingshot API expects "workspaceId" to be in camelCase, the
        # rest of the keys are in snake_case.
        if workspace_id is not UNSET:
            json["workspaceId"] = workspace_id
        if description is not UNSET:
            json["description"] = description

        if settings is not UNSET and settings is not None:
            json["settings"] = {}
            for key in (
                "sla_minutes",
                "fix_scaling_type",
                "auto_apply_recs",
                "optimize_instance_size",
            ):
                _dict_set_if_not_unset(settings, json["settings"], key)
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

    def delete(self, project_id: str) -> None:
        """Delete a Slingshot project by its ID.

        This method removes the Slingshot project but does not affect the
        Databricks job that was associated with the project.

        Args:
            project_id (str): The ID of the Slingshot project to delete.

        Returns:
            None
        """
        self.client._api_request(method="DELETE", endpoint=f"/v1/projects/{project_id}")
        return None

    def reset(self, project_id: str) -> None:
        """Reset a Slingshot project by its ID, removing all previous job run data from the project.

        Use this method to clear all previous job run data and start fresh with
        the same project. It is useful when a job changes significantly and
        you want to re-optimize it without the influence of previous runs,
        since Slingshot uses historical run data to optimize the job.

        This does not affect the Databricks job associated with the project;
        run history will still be accessible from the Databricks platform.

        Args:
            project_id (str): The ID of the Slingshot project to reset.

        Returns:
            None
        """
        self.client._api_request(method="POST", endpoint=f"/v1/projects/{project_id}/reset")
        return None

    def get_projects(
        self,
        include: Optional[list[str]] = None,
        creator_id: Optional[str] = None,
        app_id: Optional[str] = None,
        job_id: Optional[str] = None,
        page: int = 1,
        size: int = 50,
    ) -> Page[ProjectSchema]:
        """Retrieve a paginated list of projects based on filter criteria.

        Args:
            include (Optional[list[str]]): Attributes within :class:`ProjectSchema`
                to include in the response. If not provided, all available
                attributes are included. Defaults to None.
            creator_id (Optional[str], optional): The ID of the project creator
                to filter projects by. Defaults to None.
            app_id (Optional[str], optional): The application ID to filter
                projects by. This is an identifier that is unique across all
                projects for a Slingshot subscriber and is set at the time a
                project is created. Defaults to None.
            job_id (Optional[str], optional): The Databricks job ID to filter
                projects by. Defaults to None.
            page (int, optional): The page number to retrieve. Defaults to 1.
            size (int, optional): The number of projects to retrieve per page.
                Defaults to 50.

        Returns:
            Page[ProjectSchema]: A list of project details for the requested
            page.

        """
        params: QueryParams = {
            "page": cast(str, page),
            "size": cast(str, size),
        }

        if include:
            # pyright is not happy with list[str] although QueryParams allows it
            params["include"] = include  # pyright: ignore
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
        include: Optional[list[str]] = None,
        creator_id: Optional[str] = None,
        app_id: Optional[str] = None,
        job_id: Optional[str] = None,
        size: int = 50,
        max_pages: int = MAX_PAGES,
    ) -> Iterator[ProjectSchema]:
        """Fetch all projects page by page using a memory-efficient generator.

        Args:
            include (Optional[list[str]]): Attributes within :class:`ProjectSchema`
                to include in the response. If not provided, all available
                attributes are included. Defaults to None.
            creator_id (Optional[str], optional): The ID of the project creator
                to filter projects by. Defaults to None.
            app_id (Optional[str], optional): The application ID to filter
                projects by. This is an identifier that is unique across all
                projects for a Slingshot subscriber and is set at the time a
                project is created. Defaults to None.
            job_id (Optional[str], optional): The Databricks job ID to filter
                projects by. Defaults to None.
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

    def get_project(self, project_id: str, include: Optional[list[str]] = None) -> ProjectSchema:
        """Fetch a project by its ID.

        Args:
            project_id (str): The ID of the project to fetch.
            include (Optional[list[str]]): Attributes within :class:`ProjectSchema`
                to include in the response. If not provided, all available
                attributes are included. Defaults to None.

        Returns:
            ProjectSchema: The project details.

        """
        params: QueryParams = {}
        if include:
            params["include"] = include
        response = cast(
            dict[str, Any],
            self.client._api_request(
                method="GET", endpoint=f"/v1/projects/{project_id}", params=params
            ),
        )
        return cast(ProjectSchema, response.get("result"))

    def create_recommendation(self, project_id: str) -> RecommendationDetailsSchema:
        """Create a new recommendation for a Slingshot project.

        Recommendations are suggested changes to Databricks job cluster
        configurations meant to minimize costs while keeping job run time
        within required SLAs. They are generated based on the previous job runs
        associated with the Slingshot project.

        A recommendation can be created for a project once Slingshot has
        received details about a successful job run associated with that
        project. Slingshot will begin checking for job runs after a project is
        linked to a Databricks job (or a cluster within that job).

        The recommendation will be in a "PENDING" state immediately after
        creation, meaning it is still being processed. It can be applied once
        its state is "SUCCESS".

        Note:
            The returned value, a dictionary with info about the
            recommendation, lacks the full details of the recommendation
            because the state is still "PENDING" immediately after the
            recommendation is created. Use the method
            :meth:`get_recommendation` to retrieve the full details, like
            this:

            >>> from slingshot import SlingshotClient
            >>> client = SlingshotClient()
            >>> project_id = "your_project_id"

            >>> # Create a recommendation
            >>> recommendation = client.projects.create_recommendation(project_id)
            >>> # Get the recommendation details
            >>> recommendation_details = client.projects.get_recommendation(
            >>>     project_id=project_id, recommendation_id=recommendation["id"]
            >>> )

        Args:
            project_id (str): The ID of the project to create a recommendation
                for.

        Returns:
            RecommendationDetailsSchema: A dictionary with details about the
            recommendation that was created. The recommendation will have a
            "PENDING" state, meaning it is still being processed. To get the
            full details of the recommendation, use the
            :meth:`get_recommendation` method with the recommendation ID
            returned in the response.

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

    def get_recommendation(
        self,
        project_id: str,
        recommendation_id: str,
    ) -> RecommendationDetailsSchema:
        """Fetch a specific recommendation for a Slingshot project.

        Recommendations are suggested changes to Databricks job cluster
        configurations meant to minimize costs while keeping job run time
        within required SLAs. They are generated based on the previous job runs
        associated with the Slingshot project.

        Args:
            project_id (str): The ID of the project that the recommendation
                belongs to.
            recommendation_id (str): The ID of the recommendation to fetch.

        Returns:
            RecommendationDetailsSchema: A dictionary with details of the
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

    def apply_recommendation(
        self,
        project_id: str,
        recommendation_id: str,
    ) -> RecommendationDetailsSchema:
        """Apply a recommendation to the Slingshot project.

        The recommendation is applied to the Databricks job associated
        with the Slingshot project.

        Args:
            project_id (str): The ID of the project that the recommendation
                belongs to.
            recommendation_id (str): The ID of the recommendation to fetch.

        Returns:
            RecommendationDetailsSchema: A dictionary with details of the
            recommendation that was applied.
        """
        # Apply the recommendation to the project. This raises an error if
        # unsuccessful.
        self.client._api_request(
            method="POST",
            endpoint=f"/v1/projects/{project_id}/recommendations/{recommendation_id}/apply",
        )

        # Retrieve the recommendation after successful application
        return self.get_recommendation(
            project_id=project_id,
            recommendation_id=recommendation_id,
        )
