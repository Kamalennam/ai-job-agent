# Local Development Guide

Run the app on your machine with Python and Node. Use Docker **only** for infrastructure (MongoDB, Redis, Ollama) — or install those natively.

Production and CI/CD use full `docker-compose.yml`.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 20+ |
| Docker Desktop | For infra services only |

---

## One-time setup

```powershell
cd D:\AI-Job-Agent

# Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# Frontend dependencies
npm install

# Environment (local hostnames, not Docker service names)
Copy-Item .env.local.example .env

# Start infrastructure
docker compose -f docker-compose.infra.yml up -d

# Pull Ollama model (first time only)
docker compose -f docker-compose.infra.yml exec ollama ollama pull llama3.2
```

---

## Run the app (4 terminals)

Activate the venv in each terminal: `.\.venv\Scripts\Activate.ps1`

### Terminal 1 — API

```powershell
cd D:\AI-Job-Agent\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: http://localhost:8000/docs

### Terminal 2 — Celery worker

**Windows requires `--pool=solo`:**

```powershell
cd D:\AI-Job-Agent\backend
celery -A app.workers.celery worker --queues=resume,scraping,matching --loglevel=info --pool=solo
```

### Terminal 3 — Celery beat (scheduler)

```powershell
cd D:\AI-Job-Agent\backend
celery -A app.workers.celery beat --loglevel=info
```

### Terminal 4 — Frontend

```powershell
cd D:\AI-Job-Agent
npm run dev
```

App: http://localhost:5173

---

## Makefile shortcuts

```bash
make infra-up      # Start MongoDB + Redis + Ollama
make infra-down    # Stop infrastructure
make dev-api       # Run FastAPI (from backend/)
make dev-worker    # Run Celery worker (solo pool)
make dev-beat      # Run Celery beat
make dev-frontend  # Run Vite dev server
make test-local    # Run pytest without Docker
```

---

## Local vs Docker (.env)

| Variable | Local (`.env.local.example`) | Docker (`.env.example`) |
|----------|-------------------------------|-------------------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | `mongodb://mongodb:27017` |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | `http://ollama:11434` |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `http://localhost/api/v1` |
| `UPLOAD_DIR` | `uploads` | `/app/uploads` |

---

## Verify

```powershell
curl http://localhost:8000/api/v1/health/ready
```

---

## Production / deployment

Use full Docker stack:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

See [DEPLOYMENT.md](DEPLOYMENT.md) and `.github/workflows/deploy.yml`.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial local development guide |
