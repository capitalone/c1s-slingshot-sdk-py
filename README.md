# Capital One Slingshot SDK Python Library

![Capital One Slingshot Logo](docs/_static/slingshot-small-logo.png)

- [Capital One Slingshot SDK Python Library](#capital-one-slingshot-sdk-python-library)
  - [Quick Start](#quick-start)
  - [Development Setup](#development-setup)
  - [Contribution Guidelines](#contribution-guidelines)
    - [Documentation](#documentation)
    - [Releases](#releases)
    - [Commit Message Guidelines](#commit-message-guidelines)
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
make test            # Run tests across all Python versions
make install-precommit # Install pre-commit hooks
```

### Testing Commands

```bash
make test                    # Run tests across all Python versions (3.9-3.13)
make test 3.11               # Run tests for specific Python version
make test 3.11 lowest        # Run tests with specific Python version and dependency resolution
make test 3.11 highest       # Run tests with specific Python version and highest dependency resolution
make check                   # Run full CI pipeline locally (lint, typecheck, test)
```

The testing system automatically handles different Python versions and dependency resolutions using `uv`, ensuring compatibility across your supported environment matrix.

### Utility Commands

```bash
make clean           # Clean up build artifacts and cache files
make help            # Show all available commands
```

### Commit Message Guidelines

When contributing to this project, please use the [Conventional Commit](https://www.conventionalcommits.org/) style for naming your commits. This ensures consistency and helps with automated versioning and changelog generation.

A commit message should follow this format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code restructuring without changing functionality
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (e.g., updating dependencies)

#### Examples

- `feat: add support for Python 3.13`
- `fix: resolve issue with dependency resolution`
- `docs: update README with commit guidelines`

For more details, refer to the [Conventional Commit Specification](https://www.conventionalcommits.org/).
