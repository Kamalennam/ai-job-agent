.PHONY: help up down build logs shell-api shell-worker test lint docs test-prompt \
	infra-up infra-down dev-api dev-worker dev-beat dev-frontend test-local lint-local

help:
	@echo "AI Job Agent — Development Commands"
	@echo ""
	@echo "  Local dev (Python on host, infra in Docker):"
	@echo "    make infra-up       Start MongoDB + Redis + Ollama"
	@echo "    make infra-down     Stop infrastructure"
	@echo "    make dev-api        Run FastAPI with reload"
	@echo "    make dev-worker     Run Celery worker (solo pool for Windows)"
	@echo "    make dev-beat       Run Celery beat scheduler"
	@echo "    make dev-frontend   Run Vite dev server"
	@echo "    make test-local     Run pytest without Docker"
	@echo "    make lint-local     Run ruff + frontend lint without Docker"
	@echo ""
	@echo "  Full Docker stack (production-like):"
	@echo "    make up          Start all services (docker compose)"
	@echo "    make down        Stop all services"
	@echo "    make build       Build Docker images"
	@echo "    make logs        Tail all service logs"
	@echo "    make shell-api   Open shell in API container"
	@echo "    make shell-worker Open shell in Celery worker"
	@echo "    make test        Run backend tests in Docker"
	@echo "    make lint        Run linters in Docker"
	@echo "    make test-prompt Test resume extraction prompt against Ollama"
	@echo "    make docs        Validate documentation structure"

infra-up:
	docker compose -f docker-compose.infra.yml up -d

infra-down:
	docker compose -f docker-compose.infra.yml down

dev-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	cd backend && celery -A app.workers.celery worker --queues=resume,scraping,matching --loglevel=info --pool=solo

dev-beat:
	cd backend && celery -A app.workers.celery beat --loglevel=info

dev-frontend:
	npm run dev

test-local:
	cd backend && pytest app/tests -v

lint-local:
	cd backend && ruff check app
	npm run lint

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

shell-api:
	docker compose exec api bash

shell-worker:
	docker compose exec celery-worker bash

test:
	docker compose exec api pytest backend/app/tests -v

test-prompt:
	python scripts/test_resume_extraction_prompt.py

lint:
	docker compose exec api ruff check backend/app
	docker compose exec frontend npm run lint

docs:
	@echo "Documentation index: docs/README.md"
	@test -f docs/HLD.md && test -f docs/LLD.md && echo "Blueprint docs present."
