.DEFAULT_GOAL := help

# Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := $(shell pwd)

#* Docker variables
IMAGE := 1337ft
DOCKER_VERSION := dev



# Help message
.PHONY: help
help:
	@echo "Available targets:"
	@echo "- install: Install dependencies and mypy types"
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


# Installation
.PHONY: install
install:
	uv sync
	uv run mypy --install-types --non-interactive ./

.PHONY: pre-commit-install
pre-commit-install:
	uv run pre-commit install
	uv run pre-commit run --all-files --color=always --show-diff-on-failure

# Formatters
.PHONY: codestyle
codestyle:
	uv run pyupgrade --exit-zero-even-if-changed --py311-plus **/*.py
	uv run ruff check --ignore E501 ./1337ft --fix
	uv run ruff format ./1337ft

.PHONY: format
format: codestyle

# Testing
.PHONY: test
test:
	uv run pytest tests/ -v

# Linting
.PHONY: check-codestyle
check-codestyle:
	uv run ruff check --ignore E501 ./1337ft
	uv run ruff format --check ./1337ft

.PHONY: mypy
mypy:
	uv run mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	uv run bandit -ll --recursive 1337ft tests

.PHONY: lint
lint: check-codestyle mypy check-safety

.PHONY: update-dev-deps
update-dev-deps:
	uv add --dev bandit mypy pre-commit pytest pyupgrade ruff

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
docker-run:
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

.PHONY: clean
clean: cleanup
