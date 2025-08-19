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
        "app_id": "example-app"
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

```python
from slingshot import SlingshotClient
from slingshot.exceptions import (
    SlingshotAPIError,
    SlingshotAuthenticationError,
    SlingshotNotFoundError
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_project_fetch(client: SlingshotClient, project_id: str):
    """Fetch a project with comprehensive error handling."""


def main():
    client = SlingshotClient()

    try:
        project = client.projects.get(project_id)
        logger.info(f"Successfully fetched project: {project['name']}")
        return project

    except SlingshotAuthenticationError:
        logger.error("Authentication failed. Please check your API key.")
        return None

    except SlingshotNotFoundError:
        logger.warning(f"Project with ID {project_id} not found.")
        return None

    except SlingshotAPIError as e:
        logger.error(f"API error occurred: {e.message}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    main()
```
