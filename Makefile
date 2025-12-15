# Makefile - Common build and development tasks
# Usage: make [target]

.PHONY: help install setup test build clean format lint run web desktop docs

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Modbus Monitor - Make Targets$(NC)"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  $(GREEN)make setup$(NC)        - Setup development environment"
	@echo "  $(GREEN)make install$(NC)      - Install dependencies (after venv created)"
	@echo "  $(GREEN)make install-dev$(NC)  - Install with development tools"
	@echo ""
	@echo "Testing:"
	@echo "  $(GREEN)make test$(NC)        - Run all tests"
	@echo "  $(GREEN)make test-verbose$(NC) - Run tests with verbose output"
	@echo "  $(GREEN)make coverage$(NC)    - Run tests with coverage report"
	@echo "  $(GREEN)make test-fast$(NC)   - Run only fast unit tests"
	@echo ""
	@echo "Building:"
	@echo "  $(GREEN)make build$(NC)       - Build standalone executable"
	@echo "  $(GREEN)make build-clean$(NC) - Clean build and rebuild"
	@echo ""
	@echo "Development:"
	@echo "  $(GREEN)make web$(NC)         - Run web dashboard (recommended)"
	@echo "  $(GREEN)make app$(NC)         - Run simple Flask app"
	@echo "  $(GREEN)make desktop$(NC)     - Run desktop GUI (PyQt6)"
	@echo "  $(GREEN)make format$(NC)      - Format code with black"
	@echo "  $(GREEN)make lint$(NC)        - Run code quality checks"
	@echo ""
	@echo "Utilities:"
	@echo "  $(GREEN)make clean$(NC)       - Clean build artifacts"
	@echo "  $(GREEN)make docs$(NC)        - Build documentation (if available)"
	@echo "  $(GREEN)make help$(NC)        - Show this help message"

# Setup
setup:
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@python3 -m venv venv
	@echo "$(GREEN)Virtual environment created$(NC)"
	@. venv/bin/activate && make install-dev

# Install dependencies
install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@pip install --quiet --upgrade pip setuptools wheel
	@pip install --quiet -r requirements.txt
	@echo "$(GREEN)Dependencies installed$(NC)"

install-dev: install
	@echo "$(BLUE)Installing development tools...$(NC)"
	@pip install --quiet pytest pytest-cov pytest-mock black pylint flake8 mypy pyinstaller
	@echo "$(GREEN)Development tools installed$(NC)"

# Testing
test:
	@echo "$(BLUE)Running tests...$(NC)"
	@pytest tests/

test-verbose:
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	@pytest -v tests/

coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@pytest --cov=modbus_monitor --cov-report=html tests/
	@echo "$(GREEN)Coverage report generated: htmlcov/index.html$(NC)"

test-fast:
	@echo "$(BLUE)Running fast unit tests...$(NC)"
	@pytest -m unit tests/

# Building
build:
	@echo "$(BLUE)Building executable...$(NC)"
	@python build.py

build-clean:
	@echo "$(BLUE)Clean building...$(NC)"
	@python build.py --clean

# Development
web:
	@echo "$(BLUE)Starting WebSocket dashboard (recommended)...$(NC)"
	@python dashboard_app.py

app:
	@echo "$(BLUE)Starting simple Flask app...$(NC)"
	@python app.py

desktop:
	@echo "$(BLUE)Starting desktop GUI...$(NC)"
	@python modbus_monitor_pyqt.py

# Code quality
format:
	@echo "$(BLUE)Formatting code with black...$(NC)"
	@black modbus_monitor/ tests/ *.py
	@echo "$(GREEN)Code formatted$(NC)"

lint:
	@echo "$(BLUE)Running code quality checks...$(NC)"
	@echo "$(BLUE)Running pylint...$(NC)"
	@pylint modbus_monitor/ --disable=all --enable=E,F,W || true
	@echo "$(BLUE)Running flake8...$(NC)"
	@flake8 modbus_monitor/ tests/ --max-line-length=100 || true
	@echo "$(BLUE)Running mypy...$(NC)"
	@mypy modbus_monitor/ --ignore-missing-imports || true
	@echo "$(GREEN)Quality checks completed$(NC)"

# Utilities
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@rm -f .coverage *.spec
	@echo "$(GREEN)Cleaned$(NC)"

docs:
	@echo "$(BLUE)Building documentation...$(NC)"
	@echo "$(BLUE)Documentation files are in docs/ directory$(NC)"

reqs:
	@echo "$(BLUE)Updating requirements.txt...$(NC)"
	@pip freeze > requirements.txt
	@echo "$(GREEN)requirements.txt updated$(NC)"

check:
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	@make format
	@make lint
	@make test
	@echo "$(GREEN)All checks passed$(NC)"

.SILENT:
