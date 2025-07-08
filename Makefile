# Makefile for Slingshot SDK Python project

.PHONY: help bootstrap install-uv setup-venv sync test install-precommit clean

# Default target
help:
	@echo "Available targets:"
	@echo "  bootstrap      - Full project setup (install uv, setup venv, sync deps, install pre-commit, run tests)"
	@echo "  install-uv     - Install uv if not found"
	@echo "  setup-venv     - Create virtual environment with uv"
	@echo "  sync           - Sync dependencies with uv"
	@echo "  test           - Run tests"
	@echo "  install-precommit - Install pre-commit hooks"
	@echo "  clean          - Clean up build artifacts and cache"

# Bootstrap everything
bootstrap: install-uv setup-venv sync install-precommit test
	@echo "✅ Project bootstrap completed successfully!"

# Install uv if not found
install-uv:
	@echo "🔍 Checking for uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "📦 Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed successfully"; \
	else \
		echo "✅ uv is already installed"; \
	fi

# Create virtual environment
setup-venv:
	@echo "🐍 Setting up virtual environment..."
	@uv venv
	@echo "✅ Virtual environment created"

# Sync dependencies
sync:
	@echo "📦 Syncing dependencies..."
	@uv sync --dev
	@echo "✅ Dependencies synchronized"

# Run tests
test:
	@echo "🧪 Running tests..."
	@uv run pytest
	@echo "✅ Tests completed"

# Install pre-commit hooks
install-precommit:
	@echo "🎣 Installing pre-commit hooks..."
	@uv run pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .pytest_cache/
	@rm -rf .ruff_cache/
	@rm -rf __pycache__/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info/
	@echo "✅ Cleanup completed"
