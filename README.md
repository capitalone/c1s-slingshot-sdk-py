# Capital One Slingshot SDK Python Library

![Capital One Slingshot Logo](docs/_static/slingshot-small-logo.png)

The Slingshot Library provides drop-in functions facilitating integration between Slingshot's API and existing Apache Spark orchestrations. Integration enables tracking of high-level job metrics to provide optimized configurations to help meet SLAs while keeping costs down.

*Note*: This library is under active development and may contain features not yet fully supported.

- [Capital One Slingshot SDK Python Library](#capital-one-slingshot-sdk-python-library)
  - [Quick Start](#quick-start)
  - [Development Setup](#development-setup)
  - [Contribution Guidelines](#contribution-guidelines)
    - [Documentation](#documentation)
    - [Releases](#releases)
  - [CLI](#cli)
  - [Developer Interface](#developer-interface)
  - [Configuration](#configuration)

## Quick Start

To get started with the Slingshot SDK, you can use the provided Makefile for easy setup:

```bash
make bootstrap
```

This single command will:
- Install `uv` if not already available
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks
- Run the test suite

## Development Setup

The project uses a Makefile to streamline common development tasks. Here are the available commands:

### Bootstrap Everything
```bash
make bootstrap
```
Complete project setup - this is what you want to run first!

### Individual Setup Steps
```bash
make install-uv      # Install uv package manager if not found
make setup-venv      # Create virtual environment with uv
make sync            # Sync dependencies with uv
make test            # Run the test suite
make install-precommit # Install pre-commit hooks
```

### Utility Commands
```bash
make clean           # Clean up build artifacts and cache files
make help            # Show all available commands
```

## Contribution Guidelines

Only add what provides clear benefit - no speculative development. Contributions should be organized in well-defined orthogonal functions and classes - "building blocks" - with documentation and tests. Public functions are subject to the constraints of [semantic versioning](https://semver.org). And be nice!

### Documentation

Documentation for consumers of the library is built using [Sphinx](https://www.sphinx-doc.org/en/master/). Pages are defined in [reStructuredText](https://docutils.sourceforge.io/rst.html) which may pull in reStructuredText from docstrings in the code. The VS Code extension, autoDocstring, provides a convenient way to initialize function docstrings. For compatibility, set the docstring format in the extension's settings to "sphinx". Information is meaningless without context so sprinkle documentation liberally with refs: [Cross-referencing with Sphinx](https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html), [Cross-referencing Python objects](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#cross-referencing-python-objects).

When code is merged to `main` a Github action automatically deploys the documentation to Github Pages. Click "View deployment" in the "github-pages" environment of this repo to navigate to the latest documentation. There's also a shortcut in the "About" section of the Github repo page.

To make sure documentation updates appear as intended before merging you can build and view it locally like,

``` bash
% cd docs
% make html
% open _build/html/index.html
```

For troubleshooting documentation issues it may help to remove the "\_build" directory and all its content (`rm -rf _build`).

### Releases

Releases are semi-automated with the "Release new library version" Github workflow. To cut a new release update the version in [`slingshot/__init__.py`](slingshot/__init__.py) in a PR. Once it's merged run the "Release new library version" workflow on `main` from the "Actions" tab of the Github page for this repo. This will tag `main` with the new version, update the `latest` tag to match and create a Github release.

## CLI

The CLI is provided mainly for demonstration of what's possible when you integrate with Slingshot's API using this library. Explore available commands with `slingshot --help`

## Developer Interface

The developer interface consists of the public attributes of the `slingshot.api` package, and the `slingshot.awsazure` and `slingshot.awsdatabricks` modules. With each change the impact to the version of the next release must be considered in regard to semantic versioning [semantic versioning](https://semver.org). The developer interface is built using clients including those in `slingshot.clients`. Clients in that package provide a raw interface to their corresponding services and are intended to support the developer interface only.

This library is organized by functional domain as hinted by the names of the modules under the `slingshot` package. Utilities for interacting with Databricks are in `slingshot.awsazure` and `slingshot.awsdatabricks`, respectively. These modules will provide functionality for starting jobs and consolidating information required for Slingshot predictions. When starting jobs tags are applied and the event log location specified.

Successful responses and errors from the developer interface will be returned in an instance of the generic [Response](slingshot/models.py). Use of this model means that exceptions raised must be handled by this library to provide helpful information in the error response.

## Configuration

Configuration at the installation site is required before the library can be used. See the user guide for details.