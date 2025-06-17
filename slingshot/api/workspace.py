from slingshot.clients.slingshot import get_default_client
from slingshot.models import Response


def onboard_job(workspace_id: str, job_id: str, project_id: str) -> Response[str]:
    return Response(**get_default_client().onboard_workflow(workspace_id, job_id, project_id))
