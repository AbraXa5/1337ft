.DEFAULT_GOAL := help

# Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := $(shell pwd)
POETRY_VERSION := 1.5.0

#* Docker variables
IMAGE := 1337ft
DOCKER_VERSION := dev



# Help message
.PHONY: help
help:
	@echo "Available targets:"
	@echo "- poetry-download: Download and install Poetry"
	@echo "- poetry-remove: Remove Poetry from the system"
	@echo "- install: Install dependencies and install mypy types"
	@echo "- pre-commit-install: Install pre-commit hooks"
	@echo "- codestyle: Apply code formatting"
	@echo "- format: Alias for codestyle"
	@echo "- check-codestyle: Check code style without modifying files"
	@echo "- mypy: Run static type checking"
	@echo "- check-safety: Check for security vulnerabilities"
	@echo "- lint: Run all linting checks"
	@echo "- update-dev-deps: Update development dependencies"
	@echo "- docker-build: Build Docker image"
	@echo "- docker-remove: Remove Docker image"
	@echo "- docker-run: Run the docker image"
	@echo "- cleanup: Remove temporary files and directories"
	@echo "- clean: Alias for cleanup"


# Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --version $(POETRY_VERSION)

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

# Installation
.PHONY: install
install:
	poetry install --no-interaction
	poetry run mypy --install-types --non-interactive ./

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install
	poetry run pre-commit run --all-files --color=always --show-diff-on-failure

# Formatters
.PHONY: codestyle
codestyle:
#poetry run pyupgrade --exit-zero-even-if-changed --py310-plus **/*.py
	poetry run ruff check --ignore E501 ./1337ft --fix
	poetry run isort --settings-path pyproject.toml ./1337ft
	poetry run black --config pyproject.toml ./1337ft

.PHONY: format
format: codestyle

# Linting
.PHONY: check-codestyle
check-codestyle:
	poetry run ruff check --ignore E501 ./1337ft
	poetry run isort --diff --check-only --settings-path pyproject.toml ./1337ft
	poetry run black --diff --check --config pyproject.toml ./1337ft

.PHONY: mypy
mypy:
	poetry run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	poetry check
# poetry run safety check --full-report
	bandit -ll --recursive 1337ft tests

.PHONY: lint
lint: check-codestyle mypy check-safety

.PHONY: update-dev-deps
update-dev-deps:
	poetry add -G dev black@latest bandit@latest "isort[colors]@latest" mypy@latest pre-commit@latest \
	pytest@latest pyupgrade@latest

# Docker
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(DOCKER_VERSION) ...
	docker build \
		-t $(IMAGE):$(DOCKER_VERSION) .

.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(DOCKER_VERSION) ...
	docker rmi -f $(IMAGE):$(DOCKER_VERSION)

.PHONY: docker-run
docker-run: ## Create an alias for running 1337ft_docker
	@echo "Running the 1337ft docker image..."
	docker run -d --rm -p 8008:8008 --name 1337ft 1337ft:dev

# Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . -type d -name '__pycache__' -exec rm -rf {} +

.PHONY: ruff-remove
ruff-remove:
	find . -type f -name '.ruff_cache' -exec rm -f {} +

.PHONY: mypycache-remove
mypycache-remove:
	find . -type d -name '.mypy_cache' -exec rm -rf {} +

.PHONY: pytestcache-remove
pytestcache-remove:
	find . -type d -name '.pytest_cache' -exec rm -rf {} +

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove ruff-remove mypycache-remove pytestcache-remove build-remove
