# Capital One Slingshot SDK Python Library

![Capital One Slingshot Logo](https://raw.githubusercontent.com/capitalone/c1s-slingshot-sdk-py/main/docs/_static/slingshot-small-logo.png)

The official Python SDK for Capital One's Slingshot platform. This library provides a convenient way to interact with the Slingshot API from your Python applications.

## 📚 Documentation

**➤ [Complete Documentation & API Reference](https://capitalone.github.io/c1s-slingshot-sdk-py/)**

For comprehensive guides, examples, and API documentation, visit our GitHub Pages documentation site.

## Table of Contents

- [Capital One Slingshot SDK Python Library](#capital-one-slingshot-sdk-python-library)
  - [📚 Documentation](#-documentation)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

Install the SDK using pip:

```bash
pip install c1s-slingshot-sdk-py
```

## Quick Start

```python
from slingshot import SlingshotClient

# Initialize the client (uses SLINGSHOT_API_KEY environment variable)
client = SlingshotClient()

# List projects
all_projects = []
for project in client.projects.iterate_projects(include=[]):
    all_projects.append(project)
print(f"Found {len(all_projects)} projects.")
```

## Contributing

> [!IMPORTANT]
> At this time, we are only accepting pull requests from Capital One employees. External pull requests will be closed.

🔧 **[Contributing Guide](CONTRIBUTING.md)** - Development setup, testing, and release process

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
