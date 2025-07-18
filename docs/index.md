# Capital One Slingshot SDK Python Library

Welcome to the Capital One Slingshot SDK documentation!

```{toctree}
:maxdepth: 2
:caption: Contents:

quickstart
api
examples
changelog
```

## Overview

The Capital One Slingshot SDK provides a Python interface for interacting with the Slingshot API. This SDK simplifies authentication, request handling, and response processing for developers building applications that integrate with Capital One's Slingshot platform.

## Features

- **Simple API Client**: Easy-to-use client for making authenticated requests
- **Type Safety**: Full type hints for better IDE support and code safety
- **Error Handling**: Comprehensive exception handling with meaningful error messages
- **Retry Logic**: Built-in retry mechanisms for resilient API interactions
- **Async Support**: Asynchronous operations for better performance

## Installation

```bash
pip install c1s-slingshot-sdk-py
```

## Quick Example

```python
from slingshot import SlingshotClient

# Initialize the client
client = SlingshotClient(api_key="your-api-key")

# Use the client to interact with the API
projects = client.projects.list()
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
