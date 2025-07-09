# Makefile for Slingshot SDK Python project

.PHONY: help bootstrap install-uv setup-venv sync test install-precommit clean changelog commit

# Default target
help:
	@echo "Available targets:"
	@echo "  bootstrap      - Full project setup (install uv, setup venv, sync deps, install pre-commit, run tests)"
	@echo "  install-uv     - Install uv if not found"
	@echo "  setup-venv     - Create virtual environment with uv"
	@echo "  sync           - Sync dependencies with uv"
	@echo "  test           - Run tests"
	@echo "  install-precommit - Install pre-commit hooks"
	@echo "  commit         - Interactive conventional commit"
	@echo "  changelog      - Generate changelog from git commits"
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
	@uv run pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
	@echo "✅ Pre-commit hooks installed"

# Interactive conventional commit
commit:
	@echo "📝 Creating conventional commit..."
	@uv run cz commit

# Generate changelog from git commits
changelog:
	@echo "📝 Generating changelog from git commits..."
	@git log --oneline --decorate --graph --since="$(shell git describe --tags --abbrev=0 2>/dev/null || echo '1 year ago')" --pretty=format:"- %s (%h)" > CHANGELOG_TEMP.md
	@echo "✅ Changelog generated in CHANGELOG_TEMP.md"
	@echo "📋 Review and merge into CHANGELOG.md manually"

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
