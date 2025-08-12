# Makefile for GrBackend project
# Provides linting, formatting, and Docker commands.

# ==============================================================================
# Docker Configuration
# ==============================================================================
# !!! IMPORTANT !!!
# Replace these placeholder values with your actual GCP configuration.
GCP_PROJECT_ID = gemini-api-lithuania
GCP_REGION = europe-central2
IMAGE_NAME = product-genie
IMAGE_TAG ?= latest
IMAGE_URL = $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(IMAGE_NAME)/$(IMAGE_NAME):$(IMAGE_TAG)


# ==============================================================================
# Development Environment
# ==============================================================================
# Variables
VENV_DIR = .venv

.PHONY: setup
setup:
	@echo "========== Setting up development environment =========="
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		uv venv $(VENV_DIR); \
	fi
	@echo "Installing dependencies..."
	@uv sync --dev

# ==============================================================================
# Linting and Formatting
# ==============================================================================
.PHONY: check
check: setup
	@exit_code=0; \
	path="."; \
	if [ -n "$(module)" ]; then path="$(module)"; fi; \
	@echo "========== Running mypy on $$path =========="; \
	uv run --no-sync mypy $$path || exit_code=1; \
	@echo "========== Running ruff check on $$path =========="; \
	uv run --no-sync ruff check $$path || exit_code=1; \
	@echo "========== Running ruff format check on $$path =========="; \
	uv run --no-sync ruff format --check --diff $$path || exit_code=1; \
	exit $$exit_code

.PHONY: fix
fix: setup
	@exit_code=0; \
	path="."; \
	if [ -n "$(module)" ]; then path="$(module)"; fi; \
	@echo "========== Running ruff check --fix on $$path =========="; \
	uv run --no-sync ruff check --fix --show-fixes $$path || exit_code=1; \
	@echo "========== Running ruff format on $$path =========="; \
	uv run --no-sync ruff format $$path || exit_code=1; \
	exit $$exit_code

# ==============================================================================
# Docker Commands
# ==============================================================================
.PHONY: build
build:
	@echo "========== Building Docker image: $(IMAGE_URL) =========="
	@docker build --platform linux/amd64 -t $(IMAGE_URL) .

.PHONY: push
push:
	@echo "========== Pushing Docker image to GCP Artifact Registry =========="
	@echo "Authenticating with GCP..."
	@gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev
	@echo "Pushing image: $(IMAGE_URL)"
	@docker push $(IMAGE_URL)


# ==============================================================================
# Miscellaneous
# ==============================================================================
.PHONY: clean
clean:
	@echo "========== Cleaning up =========="
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  setup          - Set up development environment and install dependencies"
	@echo "  check          - Run all linting checks (mypy, ruff check, ruff format check)"
	@echo "  fix            - Auto-fix linting issues (ruff check --fix, ruff format)"
	@echo "  build          - Build the Docker image"
	@echo "  push           - Push the Docker image to GCP Artifact Registry"
	@echo "  clean          - Clean up cache files and bytecode"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Optional parameters:"
	@echo "  module=<name>  - Run checks/fixes on specific module (e.g., make check module=src)"
	@echo "  IMAGE_TAG=<tag> - Specify a tag for the Docker image (default: latest)"
	@echo ""
	@echo "Examples:"
	@echo "  make check              # Check entire project"
	@echo "  make check module=src   # Check only src directory"
	@echo "  make fix                # Fix issues in entire project"
	@echo "  make fix module=utils   # Fix issues in utils directory"
	@echo "  make build              # Build Docker image with 'latest' tag"
	@echo "  make build IMAGE_TAG=v1.0 # Build Docker image with 'v1.0' tag"
	@echo "  make push               # Push 'latest' Docker image"
	@echo "  make push IMAGE_TAG=v1.0  # Push 'v1.0' Docker image"