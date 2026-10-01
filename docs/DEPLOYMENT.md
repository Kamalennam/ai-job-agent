# Deployment Guide — AI Job Agent

**Version**: 0.2.0  
**Last Updated**: 2026-07-10

---

## Local Development vs Production

| Mode | Compose file | API URL | When |
|------|--------------|---------|------|
| **Local dev** | — (Python on host) | `http://localhost:8000` | Daily coding |
| **Local Docker** | `docker-compose.yml` | `http://localhost:8000` | Full stack on machine |
| **Hostinger prod** | `docker-compose.prod.yml` | `http://187.127.146.159:8001` | Production server |

See [LOCAL_DEV.md](LOCAL_DEV.md) for the local workflow and `.env.local.example`.

### Hostinger deployment

On the server:

```bash
cp .env.production.example .env
# Edit .env with real secrets and your server IP/domain

docker compose -f docker-compose.prod.yml up -d --build
```

Required production `.env` values (template: `.env.production.example`):

```env
APP_ENV=production
API_BASE_URL=http://187.127.146.159
VITE_API_BASE_URL=/api/v1
```

Do **not** create `.env.local` on the server — that file is for laptop development only.

`VITE_API_BASE_URL` is baked into the frontend image at **build time** — rebuild after changing it.

**Important:** `docker compose restart` does **not** reload `.env` changes. After editing `.env`, recreate containers:

```bash
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

In Docker, use `PROMPTS_DIR=prompts` or `PROMPTS_DIR=/app/prompts` (both resolve to `/app/prompts` when prompts are mounted there). Do **not** use `/prompts` — that path does not exist in the container.

---

## Environments

| Environment | Orchestration | Purpose |
|-------------|--------------|---------|
| `development` | Docker Compose (local) | Local dev with hot reload |
| `staging` | Docker Compose (EC2) | Pre-production testing |
| `production` | Docker Compose (EC2) | Self-hosted production |

---

## Docker Compose Services

File: `docker-compose.yml`

| Service | Image | Port | Replicas |
|---------|-------|------|----------|
| `nginx` | nginx:alpine | 80 | 1 |
| `frontend` | build: frontend/ | 5173 | 1 |
| `api` | build: backend/ | 8000 | 1 |
| `celery-worker` | build: backend/ | — | 1 (scale to 4) |
| `celery-beat` | build: backend/ | — | 1 |
| `mongodb` | mongo:7 | 27017 | 1 |
| `redis` | redis:7-alpine | 6379 | 1 |
| `ollama` | ollama/ollama | 11434 | 1 |

### Optional (Monitoring)

| Service | Image | Port |
|---------|-------|------|
| `prometheus` | prom/prometheus | 9090 |
| `grafana` | grafana/grafana | 3000 |

---

## Quick Start

```bash
# 1. Clone and configure
git clone <repo-url> AI-Job-Agent
cd AI-Job-Agent
cp .env.example .env
# Edit .env with your values

# 2. Pull Ollama models
docker compose up -d ollama
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull nomic-embed-text

# 3. Start all services
make up

# 4. Verify
curl http://localhost:8000/api/v1/health/ready
```

---

## Volumes

| Volume | Mount Point | Purpose |
|--------|------------|---------|
| `mongo-data` | `/data/db` | MongoDB persistence |
| `redis-data` | `/data` | Redis persistence |
| `ollama-data` | `/root/.ollama` | Ollama models |
| `uploads` | `/app/uploads` | Resume files |
| `playwright-data` | `/app/playwright-data` | Browser profiles |
| `logs` | `/app/logs` | Application logs |

---

## Nginx Configuration

File: `docker/nginx/nginx.conf`

```
/               → frontend:5173
/api/           → api:8000
/docs           → api:8000/docs
/uploads/       → api:8000/static/uploads
```

SSL: Let's Encrypt via Certbot (production). Config in `docker/nginx/ssl/`.

---

## Celery Worker Deployment

Single `celery-worker` container runs all queues. For production, scale:

```bash
docker compose up -d --scale celery-worker=4
```

Worker startup command:
```bash
celery -A app.workers.celery worker \
  --queues=resume,scraping,matching,ai,ats,analytics,notifications,maintenance \
  --concurrency=4 \
  --loglevel=info
```

Celery Beat:
```bash
celery -A app.workers.celery beat --loglevel=info
```

---

## GitHub Actions CI/CD

Workflows live in `.github/workflows/` (see also `infrastructure/github-actions/README.md`).

| File | Trigger | Actions |
|------|---------|---------|
| `ci.yml` | PR + push to main | ruff, pytest, frontend build, docker build |
| `deploy.yml` | tag `v*` | build images, optional SSH deploy to EC2 |

### Pipeline Stages (ci.yml)

| Stage | Actions |
|-------|---------|
| Backend lint + test | ruff, pytest |
| Frontend build | `npm ci`, `npm run build` |
| Docker build | build api + frontend images, validate compose (main only) |

### Deploy (deploy.yml)

Set repository variable `ENABLE_SSH_DEPLOY=true` to enable SSH deployment.

### Required Secrets

| Secret | Purpose |
|--------|---------|
| `EC2_HOST` | Production server IP |
| `EC2_SSH_KEY` | SSH private key |
| `DOCKER_REGISTRY` | Container registry URL |

---

## Production EC2 Setup

### Recommended Instance

| Spec | Minimum | Recommended |
|------|---------|-------------|
| Instance | t3.xlarge | t3.2xlarge |
| RAM | 16 GB | 32 GB |
| Storage | 100 GB SSD | 250 GB SSD |
| GPU | — | Optional for Ollama |

### Setup Steps

1. Launch EC2 with Ubuntu 22.04
2. Install Docker + Docker Compose
3. Clone repo, configure `.env` for production
4. Configure Nginx SSL with Certbot
5. `docker compose -f docker-compose.yml up -d`
6. Configure GitHub Actions deploy

---

## Environment-Specific Configuration

| Variable | Development | Production |
|----------|-------------|------------|
| `APP_DEBUG` | `true` | `false` |
| `APP_ENV` | `development` | `production` |
| `CORS_ORIGINS` | `http://localhost:5173` | `https://yourdomain.com` |
| `PLAYWRIGHT_HEADLESS` | `true` | `true` |
| `PROMETHEUS_ENABLED` | `false` | `true` |

---

## Health Monitoring

| Check | Endpoint | Interval |
|-------|----------|----------|
| API liveness | `/api/v1/health/live` | 30s |
| API readiness | `/api/v1/health/ready` | 60s |
| Celery workers | Flower (v2) or scheduler logs | 5min |
| Disk space | OS monitoring | 15min |
| Ollama models | `/api/v1/health/ready` ollama check | 5min |

---

## Rollback Procedure

```bash
# On EC2
cd AI-Job-Agent
git checkout <previous-tag>
docker compose build
docker compose up -d
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-07-10 | Local dev guide, GitHub Actions workflows in `.github/workflows/` |
| 0.1.0 | 2026-07-10 | Initial deployment guide |
