from slingshot.client import SlingshotClient


def test_get_project(client: SlingshotClient) -> None:
    """Test fetching a project by its ID."""
    project_id = "test-project-id"

    client.projects.get_project(project_id=project_id)
    client.projects.create_project(payload={"id": project_id, "name": "Test Project"})
    project = client.projects.get_project(project_id=project_id)
    assert project["id"] == project_id
