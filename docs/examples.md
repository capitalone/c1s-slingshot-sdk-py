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
    projects = client.projects.list()
    for project in projects:
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

    # Delete the project
    print("\nDeleting the project:")
    client.projects.delete(new_project['id'])
    print("Project deleted successfully")

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

def main():
    client = SlingshotClient()

    # Try to fetch an existing project
    project = robust_project_fetch(client, "existing-project-id")
    if project:
        print(f"Found project: {project['name']}")

    # Try to fetch a non-existent project
    project = robust_project_fetch(client, "non-existent-id")
    if not project:
        print("Project not found, as expected")

if __name__ == "__main__":
    main()
```

## Advanced Examples

### Batch Operations

```python
from slingshot import SlingshotClient
from typing import List, Dict, Any
import time

def batch_create_projects(
    client: SlingshotClient,
    project_configs: List[Dict[str, Any]],
    batch_size: int = 5
) -> List[Dict[str, Any]]:
    """Create multiple projects in batches to avoid rate limiting."""
    created_projects = []

    for i in range(0, len(project_configs), batch_size):
        batch = project_configs[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}...")

        for config in batch:
            try:
                project = client.projects.create(config)
                created_projects.append(project)
                print(f"  Created: {project['name']}")
            except Exception as e:
                print(f"  Failed to create {config['name']}: {e}")

        # Add delay between batches to respect rate limits
        if i + batch_size < len(project_configs):
            print("  Waiting before next batch...")
            time.sleep(1)

    return created_projects

def main():
    client = SlingshotClient()

    # Define multiple projects to create
    projects_to_create = [
        {"name": f"Batch Project {i}", "app_id": f"batch-app-{i}"}
        for i in range(1, 11)
    ]

    # Create projects in batches
    created = batch_create_projects(client, projects_to_create)
    print(f"\nSuccessfully created {len(created)} projects")

if __name__ == "__main__":
    main()
```

### Configuration Management

```python
from slingshot import SlingshotClient
from typing import Optional
import os
from dataclasses import dataclass

@dataclass
class SlingshotConfig:
    """Configuration class for Slingshot client."""
    api_key: Optional[str] = None
    api_url: str = "https://slingshot.capitalone.com/prod/api/gradient"
    timeout: int = 30
    retries: int = 3

    @classmethod
    def from_environment(cls) -> "SlingshotConfig":
        """Create configuration from environment variables."""
        return cls(
            api_key=os.getenv("SLINGSHOT_API_KEY"),
            api_url=os.getenv("SLINGSHOT_API_URL", cls.api_url),
            timeout=int(os.getenv("SLINGSHOT_TIMEOUT", str(cls.timeout))),
            retries=int(os.getenv("SLINGSHOT_RETRIES", str(cls.retries)))
        )

def create_configured_client() -> SlingshotClient:
    """Create a client with configuration from environment."""
    config = SlingshotConfig.from_environment()

    if not config.api_key:
        raise ValueError("SLINGSHOT_API_KEY environment variable is required")

    return SlingshotClient(
        api_key=config.api_key,
        api_url=config.api_url
    )

def main():
    try:
        client = create_configured_client()

        # Test the connection
        projects = client.projects.list()
        print(f"Successfully connected! Found {len(projects)} projects.")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
```

## Testing Examples

### Mock Testing

```python
import pytest
from unittest.mock import Mock, patch
from slingshot import SlingshotClient

class TestSlingshotIntegration:
    """Example test cases for Slingshot SDK."""

    @patch('slingshot.client.httpx.Client')
    def test_list_projects_success(self, mock_httpx):
        """Test successful project listing."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "1", "name": "Project 1", "app_id": "app1"},
            {"id": "2", "name": "Project 2", "app_id": "app2"}
        ]
        mock_response.status_code = 200
        mock_httpx.return_value.get.return_value = mock_response

        # Test the client
        client = SlingshotClient(api_key="test-key")
        projects = client.projects.list()

        assert len(projects) == 2
        assert projects[0]["name"] == "Project 1"

    @patch('slingshot.client.httpx.Client')
    def test_create_project_success(self, mock_httpx):
        """Test successful project creation."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "new-id",
            "name": "New Project",
            "app_id": "new-app"
        }
        mock_response.status_code = 201
        mock_httpx.return_value.post.return_value = mock_response

        # Test the client
        client = SlingshotClient(api_key="test-key")
        project = client.projects.create({
            "name": "New Project",
            "app_id": "new-app"
        })

        assert project["id"] == "new-id"
        assert project["name"] == "New Project"

# Run with: python -m pytest test_examples.py
```

## Integration Examples

### Using with Async Frameworks

```python
import asyncio
import httpx
from typing import List, Dict, Any

class AsyncSlingshotClient:
    """Example async wrapper for Slingshot operations."""

    def __init__(self, api_key: str, api_url: str = "https://slingshot.capitalone.com/prod/api/gradient"):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def list_projects(self) -> List[Dict[str, Any]]:
        """Async project listing."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/projects",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Async project retrieval."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/projects/{project_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

async def main():
    """Example async usage."""
    client = AsyncSlingshotClient(api_key="your-api-key")

    # Fetch multiple projects concurrently
    projects = await client.list_projects()

    # Get details for first 3 projects concurrently
    if projects:
        project_ids = [p["id"] for p in projects[:3]]
        detailed_projects = await asyncio.gather(
            *[client.get_project(pid) for pid in project_ids]
        )

        for project in detailed_projects:
            print(f"Project: {project['name']}")

if __name__ == "__main__":
    asyncio.run(main())
```
