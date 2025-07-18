# Documentation

This directory contains the Sphinx documentation for the Slingshot SDK.

## Building Locally

To build the documentation locally:

```bash
# Install documentation dependencies
uv sync --group docs

# Build the documentation
make docs

# Serve the documentation locally
make docs-serve
```

The documentation will be available at `http://localhost:8000`.

## Structure

- `conf.py` - Sphinx configuration
- `index.md` - Main documentation index
- `quickstart.md` - Quick start guide
- `api.md` - API reference
- `examples.md` - Usage examples
- `contributing.md` - Contributing guidelines
- `changelog.md` - Project changelog
- `_static/` - Static assets (images, CSS, etc.)
- `_templates/` - Custom Sphinx templates
- `_build/` - Generated documentation output (git-ignored)

## Deployment

Documentation is automatically built and deployed to GitHub Pages when:
- Changes are pushed to the `main` branch
- A new version tag is created (e.g., `v1.0.0`)

The deployment uses GitHub Actions and the workflow is defined in `.github/workflows/docs.yml`.
