# Contributing to Slingshot SDK

Thank you for your interest in contributing to the Capital One Slingshot SDK! This guide provides information for developers working on the SDK itself.

> **Important**: At this time, we are only accepting pull requests from Capital One employees. Pull requests from external contributors will be closed.

📖 **Looking to use the SDK?** Check out the [README.md](README.md) for installation and usage instructions.

## Table of Contents

- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Release Process](#release-process)
- [Commit Guidelines](#commit-guidelines)

## Development Setup

The project uses a Makefile to streamline common development tasks.

### Bootstrap Everything

```bash
make bootstrap
```

This single command will:

- Install `uv` if not already available
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks
- Run the test suite

### Individual Setup Steps

If you prefer to run setup steps individually:

```bash
make clean           # Cleans up environment if procedure has already run
make install-python  # Install pyenv and necessary python versions if not found
make install-uv      # Install uv package manager if not found
make setup-venv      # Create virtual environment with uv
make sync            # Sync dependencies with uv
make install-precommit # Install pre-commit hooks
make test            # Run tests across all Python versions

```

### Available Commands

```bash
make help            # Show all available commands
make clean           # Clean up build artifacts and cache files
make docs            # Build documentation with Sphinx
make docs-serve      # Build and serve documentation locally
```

## Testing

### Testing Commands

```bash
make test                    # Run tests across all Python versions (3.9-3.13)
make test 3.11               # Run tests for specific Python version
make test 3.11 lowest        # Run tests with specific Python version and dependency resolution
make test 3.11 highest       # Run tests with specific Python version and highest dependency resolution
make check                   # Run full CI pipeline locally (lint, typecheck, test)
```

The testing system automatically handles different Python versions and dependency resolutions using `uv`, ensuring compatibility across your supported environment matrix.

## Code Quality

The project uses several tools to maintain code quality:

- **Ruff** - Linting and formatting
- **Pyright** - Type checking
- **Pre-commit hooks** - Automated checks before commits

### Pre-commit Hooks

Pre-commit hooks are automatically installed during setup and will run:

- Ruff linting and formatting
- Pyright type checking
- Conventional commit message validation
- Basic file checks (trailing whitespace, YAML validation, etc.)

### Manual Quality Checks

```bash
make check           # Run full CI pipeline locally (lint, typecheck, test)
```

## Release Process

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for automated version management and release workflows.

### How Releases Work

1. **Automatic Version Bumping**: When commits are pushed to the `main` branch, a GitHub Action automatically:
   - Analyzes commit messages using [Conventional Commit](https://www.conventionalcommits.org/) format
   - Determines the next version based on the types of changes (feat, fix, etc.)
   - Creates a pull request with version bumps and changelog updates

2. **Manual Release Creation**: Once the version bump PR is merged:
   - Create and push a git tag with the new version (e.g., `v0.5.0`)
   - This triggers the release workflow that:
     - Builds the package with `uv build`
     - Publishes to PyPI automatically
     - Builds and deploys documentation to GitHub Pages
     - Creates a GitHub release

### Creating a Release

To create a new release:

1. **Wait for the automated PR**: After pushing commits to `main`, a GitHub Action will create a PR with version bumps
2. **Review and merge the PR**: The PR will contain updated versions and changelog
3. **Create a GitHub Release**:
   - Go to the [Releases page](https://github.com/capitalone/c1s-slingshot-sdk-py/releases)
   - Click "Create a new release"
   - Create a new tag with the version (e.g., `v0.5.0`)
   - Use the version number as the release title
   - Copy the changelog content for the release description
   - Publish the release

This will trigger the automated release workflow that publishes to PyPI and deploys documentation.

### Version Management

- **Version Source**: The version is managed in `pyproject.toml`
- **Changelog**: Automatically generated in `docs/changelog.md`
- **Supported Changes**:
  - `feat:` → Minor version bump (0.4.0 → 0.5.0)
  - `fix:` → Patch version bump (0.4.0 → 0.4.1)
  - `feat!:` or `BREAKING CHANGE:` → Major version bump (0.4.0 → 1.0.0)

## Commit Guidelines

When contributing to this project, please use the [Conventional Commit](https://www.conventionalcommits.org/) style for naming your commits. This ensures consistency and helps with automated versioning and changelog generation.

A commit message should follow this format:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semi-colons, etc.)
- **refactor**: Code restructuring without changing functionality
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (e.g., updating dependencies)

### Examples

- `feat: add support for Python 3.13`
- `fix: resolve issue with dependency resolution`
- `docs: update README with commit guidelines`

For more details, refer to the [Conventional Commit Specification](https://www.conventionalcommits.org/).

## Documentation

Documentation is built using Sphinx and automatically deployed to GitHub Pages on releases.

### Building Documentation Locally

```bash
make docs            # Build documentation
make docs-serve      # Build and serve documentation locally at http://localhost:8000
make docs-clean      # Clean documentation build artifacts
```

The documentation source files are in the `docs/` directory and include:

- API reference documentation
- Quick start guide
- Examples
- Changelog

## Project Structure

```text
├── src/slingshot/          # Main SDK source code
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Main client class
│   ├── types.py           # Type definitions
│   └── api/               # API endpoint implementations
├── tests/                 # Test suite
├── docs/                  # Documentation source
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
├── Makefile              # Development commands
└── .pre-commit-config.yaml # Pre-commit configuration
```

## Getting Help

- Check the [GitHub Issues](https://github.com/capitalone/c1s-slingshot-sdk-py/issues) for existing problems or feature requests
- Review the [project documentation](https://capitalone.github.io/c1s-slingshot-sdk-py/)
- For SDK usage questions, see the [README.md](README.md)

**Note**: Only Capital One employees can submit pull requests. External contributors should use issues and discussions for feedback and suggestions.
