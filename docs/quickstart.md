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

# List all projects
projects = client.projects.get_projects()
print(f"Found {len(projects)} projects")

# Get a specific project
project = client.projects.get("project-id")
print(f"Project: {project['name']}")

# Create a new project
new_project = client.projects.create({
    "name": "My New Project",
    "app_id": "my-app"
})
```

## Error Handling

The SDK provides comprehensive error handling:

```python
from slingshot import SlingshotClient
from slingshot.exceptions import SlingshotAPIError, SlingshotAuthenticationError

client = SlingshotClient()

try:
    project = client.projects.get("invalid-id")
except SlingshotAuthenticationError:
    print("Authentication failed - check your API key")
except SlingshotAPIError as e:
    print(f"API error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

- Explore the full [API Reference](api.md)
- Check out more [Examples](examples.md)
