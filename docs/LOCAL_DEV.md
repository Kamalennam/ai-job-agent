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

# Environment (local dev on your machine — copy from .env.local.example)
Copy-Item .env.local.example .env.local

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

Resume uploads still parse when this worker is not running and Redis is down. The API runs that one task itself. Job collection and matching still need Redis and this worker.

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

## Local vs production (.env files)

**Production is unchanged** — the server keeps using `.env` only (no `.env.local` on Hostinger).

On your laptop, add **`.env.local`** for dev overrides. It loads **after** `.env`; overlapping keys win in `.env.local`.

| Where | Files used |
|-------|------------|
| Hostinger server | `.env` only |
| Your laptop | `.env` + `.env.local` (optional overrides) |

```powershell
Copy-Item .env.local.example .env.local
# Edit .env.local only if you need non-default local URLs
```

Do **not** comment/uncomment values in `.env` to switch environments.

| Variable | Override in `.env.local` |
|----------|--------------------------|
| `APP_ENV` | `development` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `llama3.1` — a model from `ollama list` on this laptop |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` |
| `STORAGE_ROOT` | `storage` |

Keep MongoDB URI, JWT, SMTP in `.env` once — shared by both environments if you use Atlas for dev.

Hostinger does not use `.env.local`. Its `.env` keeps `OLLAMA_MODEL=llama3.2` and `OLLAMA_BASE_URL=http://ollama:11434`. A resume uploaded on either side is written to that same database after that environment's Ollama finishes parsing. The PDF stays on the machine that received the upload.

---

## Local vs Docker (legacy reference)

| Variable | Local (`.env.local.example`) | Docker (full compose) |
|----------|-------------------------------|-------------------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | `mongodb://mongodb:27017` |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | `http://ollama:11434` |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | `http://localhost/api/v1` |
| `STORAGE_ROOT` | `storage` | `/app/storage` |

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
| 0.2.0 | 2026-10-08 | Resume parsing continues locally when Redis is down |
| 0.1.0 | 2026-07-10 | Initial local development guide |
