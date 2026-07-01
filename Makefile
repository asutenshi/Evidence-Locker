.DEFAULT_GOAL := help

.PHONY: help install test run run-demo docker-build docker-up

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies using uv sync"
	@echo "  make test         - Run tests using pytest"
	@echo "  make run          - Run the FastAPI application locally"
	@echo "  make run-demo     - Run the demo git collector script"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers in detached mode"
	@echo "  make help         - Show this help message"

install:
	uv sync

test:
	uv run pytest

run:
	uv run uvicorn app.main:app --reload --port 8000

run-demo:
	uv run python scripts/demo_git_collector.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
