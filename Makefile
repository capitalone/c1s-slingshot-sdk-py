# Makefile for Slingshot SDK Python project
PYTHON_VERSIONS := 3.9 3.10 3.11 3.12 3.13

.PHONY: help bootstrap install-uv setup-venv sync test check install-precommit clean

# Default target
help:
	@echo "Available targets:"
	@echo "  bootstrap      - Full project setup (install uv, setup venv, sync deps, install pre-commit, run tests)"
	@echo "  install-uv     - Install uv if not found"
	@echo "  setup-venv     - Create virtual environment with uv"
	@echo "  sync           - Sync dependencies with uv"
	@echo "  test [VERSION] [RESOLUTION] - Run tests (e.g., 'make test', 'make test 3.9', 'make test 3.9 lowest')"
	@echo "  check          - Run full CI pipeline locally (lint, typecheck, test)"
	@echo "  install-precommit - Install pre-commit hooks"
	@echo "  clean          - Clean up build artifacts and cache"

# Bootstrap everything
bootstrap: install-uv setup-venv sync
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
# Handle installing all Python versions
install-python:
# 	use pyenv as uv has issues managing python versions @ c1
	@echo "🐍 Checking for pyenv.."
	@if ! command -v pyenv >/dev/null 2>&1; then \
		echo "📦 Installing pyenv..."; \
		brew install pyenv; \
		echo "✅ pyenv installed successfully"; \
	else \
		echo "✅ pyenv is already installed"; \
	fi
	@for version in $(PYTHON_VERSIONS); do \
		echo "🐍 Installing Python $$version..."; \
		pyenv install -s $$version; \
		pyenv local $$version; \
		echo "✅ Python $$version installed successfully"; \
	done;

# Create virtual environment
setup-venv:
	@echo "🐍 Setting up virtual environment..."
	@uv venv --python 3.9
	@echo "✅ Virtual environment created"

# Sync dependencies
sync:
	@echo "📦 Syncing dependencies..."
	@uv sync --dev --resolution lowest --python 3.9
	@echo "✅ Dependencies synchronized"

# Run tests
test:
	@ARGS="$(filter-out test,$(MAKECMDGOALS))"; \
	if [ -z "$$ARGS" ]; then \
		echo "🧪 Running test matrix across all Python versions and resolutions..."; \
		for version in $(PYTHON_VERSIONS); do \
			for resolution in lowest highest; do \
				echo "🐍 Testing Python $$version with $$resolution resolution..."; \
				uv run --isolated --resolution=$$resolution --python=$$version pytest tests/ -v || exit 1; \
			done; \
		done; \
	else \
		set -- $$ARGS; \
		VERSION="$$1"; \
		RESOLUTION="$$2"; \
		if [ -n "$$VERSION" ] && [ -n "$$RESOLUTION" ]; then \
			echo "🧪 Running tests for Python $$VERSION with $$RESOLUTION resolution..."; \
			uv run --isolated --resolution=$$RESOLUTION --python=$$VERSION pytest tests/ -v; \
		elif [ -n "$$VERSION" ]; then \
			echo "🧪 Running tests for Python $$VERSION with both resolutions..."; \
			for resolution in lowest highest; do \
				echo "🐍 Testing Python $$VERSION with $$resolution resolution..."; \
				uv run --isolated --resolution=$$resolution --python=$$VERSION pytest tests/ -v || exit 1; \
			done; \
		else \
			echo "❌ Invalid arguments. Usage: make test [VERSION] [RESOLUTION]"; \
			echo "   Examples: make test, make test 3.9, make test 3.9 lowest"; \
			exit 1; \
		fi; \
	fi
	@echo "✅ Tests completed"

# Prevent make from interpreting version numbers as targets
%:
	@:

# Full CI check (lint, typecheck, test)
check:
	@echo "🚀 Running full CI pipeline locally..."
	@echo "🔍 Running pre-commit hooks..."
	@uv run pre-commit run --all-files

# Install pre-commit hooks
install-precommit:
	@echo "🎣 Installing pre-commit hooks..."
	@uv run pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
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
