# Examples

Collection of practical examples showing how to use the Slingshot SDK.

## Basic Examples

### Simple Project Management

```python
from slingshot import SlingshotClient

def main():
    # Initialize client
    client = SlingshotClient()

    # List all projects
    print("Listing all projects:")
    projects = client.projects.get_projects()
    for project in projects["items"]:
        print(f"  - {project['name']} (ID: {project['id']})")

    # Create a new project
    print("\nCreating a new project:")
    new_project = client.projects.create({
        "name": "Example Project",
        "workspace_id": "12345678901234",
        "app_id": "example-app",
    })
    print(f"Created project: {new_project['name']}")

    # Update the project
    print("\nUpdating the project:")
    updated_project = client.projects.update(new_project['id'], {
        "name": "Updated Example Project"
    })
    print(f"Updated project name: {updated_project['name']}")

if __name__ == "__main__":
    main()
```

### Error Handling Example

Slingshot SDK executes the `raise_for_status()` for all Slingshot API requests
which will raise an HTTPStatusError in the case of non-successful API requests.
Example response handling may look like the following:

```python
from slingshot import SlingshotClient
import logging
from httpx import HTTPStatusError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    client = SlingshotClient()

    try:
        project = client.projects.get(project_id)
        logger.info(f"Successfully fetched project: {project['name']}")
        return project

    except HTTPStatusError as e:
        logger.error(f"API error when fetching project {project_id}: {e.message}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error fetching Slingshot project: {str(e)}")
        return None

if __name__ == "__main__":
    main()
```
