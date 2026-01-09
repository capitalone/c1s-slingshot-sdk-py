# Quick Start

This guide will get you up and running with the Slingshot SDK in just a few minutes.

## Installation

Install the SDK using pip:

```bash
pip install c1s-slingshot-sdk-py
```

## Authentication

The Slingshot SDK requires an API key for authentication. You can provide this in several ways:

### Environment Variable (Recommended)

Set the `SLINGSHOT_API_KEY` environment variable:

```bash
export SLINGSHOT_API_KEY="your-api-key-here"
```

```python
from slingshot import SlingshotClient

# The client will automatically use the environment variable
client = SlingshotClient()
```

### Direct Initialization

Pass the API key directly when creating the client:

```python
from slingshot import SlingshotClient

client = SlingshotClient(api_key="your-api-key-here")
```

## Basic Usage

### Working with Projects

```python
from slingshot import SlingshotClient

# Initialize the client
client = SlingshotClient()

# List all Slingshot projects
all_projects = []
for project in client.projects.iterate_projects(include=[]):
    all_projects.append(project)
print(f"Found {len(all_projects)} projects.")

# Get a specific project
project = client.projects.get_project(project_id="project-id", include=["name"])
print(f"Project: {project['name']}")

# Create a new project and link it to a Databricks job compute cluster
new_project = client.projects.create(
    name="My New Project",
    workspace_id="databricks-workspace-id",
    job_id="databricks-job-id",
    cluster_path="job_clusters/step_1_cluster",
)

# Create a recommendation (available once Slingshot has received data for
# a successful Databricks job run that completed after the project was created)
recommendation = client.projects.create_recommendation(
    project_id=new_project["id"],
)

# Apply the recommendation to the Databricks job compute cluster
applied_recommendation = client.projects.apply_recommendation(
    project_id=new_project["id"],
    recommendation_id=recommendation["id"],
)
```

## Error Handling

Slingshot SDK executes the `raise_for_status()` for all Slingshot API requests
which will raise an HTTPStatusError in the case of non-successful requests.
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
        project = client.projects.get_project(project_id="project-id", include=["name"])
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

## Next Steps

- Explore the full [API Reference](api.md)
- Check out more [Examples](examples.md)
