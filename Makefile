.PHONY: help install dev test clean build run-example format lint type-check docs setup venv

# Variables
PYTHON := python3
VENV := venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
POETRY := poetry

# Default target
help:
	@echo "FIRS E-Invoice Python SDK - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        - Complete setup with venv and Poetry"
	@echo "  make venv         - Create virtual environment only"
	@echo "  make install      - Install production dependencies"
	@echo "  make dev          - Install all dependencies (including dev)"
	@echo ""
	@echo "Development:"
	@echo "  make run-example  - Run simple invoice example"
	@echo "  make test         - Run all tests"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run flake8 linter"
	@echo "  make type-check   - Run mypy type checking"
	@echo ""
	@echo "Build & Clean:"
	@echo "  make build        - Build distribution packages"
	@echo "  make docs         - Generate documentation"
	@echo "  make clean        - Clean build artifacts and cache"
	@echo "  make clean-all    - Clean everything including venv"
	@echo ""
	@echo "Poetry Commands:"
	@echo "  make poetry-update  - Update all dependencies"
	@echo "  make poetry-show    - Show installed packages"
	@echo "  make poetry-tree    - Show dependency tree"

# Setup with venv and Poetry
setup: venv
	@echo "Setting up FIRS E-Invoice SDK..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install poetry
	@$(POETRY) config virtualenvs.in-project true
	@$(POETRY) config virtualenvs.create false
	@$(POETRY) install
	@echo ""
	@echo "✓ Setup complete! Activate with: source $(VENV)/bin/activate"

# Create virtual environment
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "✓ Virtual environment created"; \
	else \
		echo "Virtual environment already exists"; \
	fi

# Install production dependencies only
install: venv
	@echo "Installing production dependencies..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install poetry
	@$(POETRY) install --no-dev
	@echo "✓ Production dependencies installed"

# Install all dependencies (including dev)
dev: venv
	@echo "Installing all dependencies..."
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install poetry
	@$(POETRY) install
	@echo "✓ All dependencies installed"

# Run tests
test:
	@echo "Running tests..."
	@$(POETRY) run pytest tests/ -v

# Run simple invoice example
run-example:
	@echo "Running simple invoice example..."
	@$(POETRY) run python examples/simple_invoice.py

# Format code
format:
	@echo "Formatting code..."
	@$(POETRY) run black firs_einvoice/
	@$(POETRY) run isort firs_einvoice/
	@echo "✓ Code formatted"

# Run linter
lint:
	@echo "Running flake8 linter..."
	@$(POETRY) run flake8 firs_einvoice/

# Run type checking
type-check:
	@echo "Running mypy type checking..."
	@$(POETRY) run mypy firs_einvoice/

# Generate documentation
docs:
	@echo "Generating documentation..."
	@$(POETRY) run sphinx-build -b html docs/ docs/_build/html
	@echo "✓ Documentation generated in docs/_build/html/"

# Build distribution packages
build: clean
	@echo "Building distribution packages..."
	@$(POETRY) build
	@echo "✓ Packages built in dist/"

# Clean build artifacts and cache
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf htmlcov/
	@rm -rf output/
	@echo "✓ Build artifacts cleaned"

# Clean everything including virtual environment
clean-all: clean
	@echo "Cleaning everything..."
	@rm -rf $(VENV)
	@rm -f poetry.lock
	@echo "✓ Everything cleaned"

# Poetry-specific commands
poetry-update:
	@echo "Updating dependencies..."
	@$(POETRY) update
	@echo "✓ Dependencies updated"

poetry-show:
	@$(POETRY) show

poetry-tree:
	@$(POETRY) show --tree

# Install pre-commit hooks (if using pre-commit)
pre-commit:
	@$(POETRY) run pre-commit install
	@echo "✓ Pre-commit hooks installed"

# Run security checks
security:
	@echo "Running security checks..."
	@$(POETRY) run pip-audit
	@echo "✓ Security checks complete"

# Create new release
release: test build
	@echo "Creating new release..."
	@echo "Don't forget to:"
	@echo "  1. Update version in pyproject.toml"
	@echo "  2. Update __version__.py"
	@echo "  3. Create git tag"
	@echo "  4. Run: poetry publish"

# Development server (if applicable)
serve:
	@echo "Starting development server..."
	@$(POETRY) run python -m http.server 8000 --directory docs/_build/html/

.DEFAULT_GOAL := help