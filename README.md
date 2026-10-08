# AI Job Agent

> An AI-powered platform that automates job discovery, resume optimization, intelligent matching, ATS applications, recruiter outreach, and analytics — governed by a documentation-first Engineering Blueprint.

## Status

**Phase: MVP in progress** — Auth, resume upload, parsing, and delete, Greenhouse job collection, resume-specific job matching, and a dashboard overview of that data are implemented. See [docs/ROADMAP.md](docs/ROADMAP.md) for remaining phases.

## Quick Start — Local Development (recommended)

Run Python and Node on your machine; use Docker only for MongoDB, Redis, and Ollama.

```powershell
# One-time setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
npm install
Copy-Item .env.local.example .env

# Start infrastructure
docker compose -f docker-compose.infra.yml up -d
```

Then open **4 terminals** (see full guide):

| Terminal | Command |
|----------|---------|
| API | `cd backend; uvicorn app.main:app --reload --port 8000` |
| Worker | `cd backend; celery -A app.workers.celery worker --queues=resume,scraping,matching --pool=solo` |
| Beat | `cd backend; celery -A app.workers.celery beat` |
| Frontend | `npm run dev` |

Full guide: **[docs/LOCAL_DEV.md](docs/LOCAL_DEV.md)**

API: http://localhost:8000/docs  
Frontend: http://localhost:5173

## Quick Start — Full Docker (production-like)

```bash
cp .env.example .env
make build
make up
```

API: `http://localhost:8000/docs`  
Frontend: `http://localhost`

## Environment Configuration

All secrets and environment-specific values live in a root `.env` file. **Never commit `.env` to version control.**

### Create your `.env`

```bash
# Local development (Python on host, Docker for infra only)
cp .env.local.example .env

# Full Docker / production-like stack
cp .env.example .env
```

Edit `.env` and replace placeholder values with your real credentials.

### Using `.env.example`

`.env.example` is the canonical list of every supported variable with safe placeholder values. It is committed to the repository and serves as documentation. When adding a new configuration field, update `.env.example`, `backend/app/config.py`, and `docs/LLD.md` §20 together.

### Required variables

These must be set or the application fails at startup with a clear validation error:

| Variable | Purpose |
|----------|---------|
| `APP_SECRET_KEY` | Application secret |
| `API_BASE_URL` | Public API origin (e.g. `http://localhost:8000`) |
| `CORS_ORIGINS` | Allowed browser origins (comma-separated) |
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB_NAME` | Database name |
| `REDIS_URL` | Redis connection |
| `CELERY_BROKER_URL` | Celery message broker |
| `CELERY_RESULT_BACKEND` | Celery result store |
| `JWT_SECRET_KEY` | JWT signing secret |
| `OLLAMA_BASE_URL` | Ollama API endpoint |
| `OLLAMA_MODEL` | Default LLM model |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model |
| `FRONTEND_BASE_URL` | Frontend URL for email verification links |
| `STORAGE_ROOT` | On-disk storage root |
| `RESUME_STORAGE_DIR` | Resume subdirectory name |

### Optional variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `APP_ENV` | `development` | `development` or `production` |
| `APP_DEBUG` | `true` | Enable debug mode |
| `SMTP_*` | empty | Email delivery; links logged to console when unset |
| `GENERATED_RESUME_DIR` | `generated-resumes` | AI resume output path |
| `COVER_LETTER_DIR` | `cover-letters` | Cover letter storage |
| `PROFILE_IMAGE_DIR` | `profile-images` | Avatar storage |
| `TEMP_DIR` | `temp` | Temporary files |
| `MAX_RESUME_SIZE_MB` | `10` | Upload size limit |
| `ALLOWED_RESUME_EXTENSIONS` | `pdf` | Permitted file types |
| `VITE_API_BASE_URL` | — | Frontend API URL (build-time) |

See [docs/LLD.md §20](docs/LLD.md#20-environment-variables) for the full reference.

### Development vs production

```bash
# Development
APP_ENV=development
APP_DEBUG=true
API_BASE_URL=http://localhost:8000

# Production
APP_ENV=production
APP_DEBUG=false
API_BASE_URL=https://api.yourdomain.com
```

Production enforces strong secrets (32+ characters) for `APP_SECRET_KEY` and `JWT_SECRET_KEY`.

### Hostinger production

On the server, use `.env.production.example` as the template:

```bash
cp .env.production.example .env
docker compose -f docker-compose.prod.yml up -d --build
```

```env
APP_ENV=production
API_BASE_URL=http://187.127.146.159:8001
VITE_API_BASE_URL=http://187.127.146.159:8001/api/v1
```

Or use Makefile shortcuts: `make prod-build` then `make prod-up`.

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR + push to main | Ruff, pytest, frontend build, Docker image build |
| `deploy.yml` | Tag `v*` | Build images + optional SSH deploy |

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production setup and secrets.

## What This Project Does

AI Job Agent is a full-stack automation platform for job seekers. It:

1. **Parses** resumes from PDF/DOCX into structured profiles
2. **Discovers** jobs from Greenhouse, Lever, Ashby, LinkedIn, Indeed, Naukri, Wellfound, and company sites
3. **Matches** each uploaded resume to collected jobs with a deterministic skill, role, experience, and project score. Embedding and LLM scoring are the next phase.
4. **Optimizes** resumes per job description for ATS compatibility
5. **Applies** to jobs via Playwright browser automation
6. **Discovers** recruiters and generates personalized outreach emails
7. **Tracks** analytics across the entire pipeline
8. **Notifies** users of matches, applications, and responses

## Documentation Index

All engineering decisions live in `docs/`. **Read these before writing any code.**

| Document | Purpose |
|----------|---------|
| [docs/PROJECT_VISION.md](docs/PROJECT_VISION.md) | North star, principles, success criteria |
| [docs/PRD.md](docs/PRD.md) | Product requirements, user stories, acceptance criteria |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phased delivery plan |
| [docs/HLD.md](docs/HLD.md) | High-level design: architecture, pipelines, stack |
| [docs/LLD.md](docs/LLD.md) | Low-level design: every module, API, collection, route |
| [docs/API_SPEC.md](docs/API_SPEC.md) | REST API contract (OpenAPI-aligned) |
| [docs/DATABASE.md](docs/DATABASE.md) | MongoDB collections, indexes, relationships |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker, CI/CD, infrastructure |
| [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) | Local Python dev (Docker for infra only) |
| [docs/SECURITY.md](docs/SECURITY.md) | Auth, secrets, compliance |
| [docs/AI_PROMPTS.md](docs/AI_PROMPTS.md) | All LLM prompt templates |
| [docs/CODING_GUIDELINES.md](docs/CODING_GUIDELINES.md) | Code standards for backend + frontend |
| [docs/TESTING.md](docs/TESTING.md) | Test strategy and coverage targets |

## Technology Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Backend REST APIs |
| MongoDB | Store resumes, jobs, analytics |
| Beanie ODM | Async MongoDB models |
| React | Frontend SPA |
| Tailwind CSS | UI styling |
| TypeScript | Frontend type safety |
| Celery | Background workers |
| Redis | Queue broker + cache |
| APScheduler | Cron scheduling |
| Playwright | Browser automation (ATS apply) |
| Ollama | Local AI inference |
| Docker | Containerization |
| Docker Compose | Local orchestration |
| Nginx | Reverse proxy |
| GitHub Actions | CI/CD |
| PyMuPDF | Resume parsing (primary) |
| pdfplumber | ATS parsing fallback |
| JWT | Authentication |
| SMTP/Gmail API | Email sending |
| Pydantic | Request/response validation |
| Loguru | Structured logging |
| Prometheus (optional) | Metrics |
| Grafana (optional) | Monitoring |

See [docs/HLD.md § Technology Stack](docs/HLD.md#3-technology-stack) for justification of every choice.

## Project Structure

```
AI-Job-Agent/
├── docs/           # Engineering Blueprint (source of truth)
├── backend/        # FastAPI application
├── frontend/       # React + Vite SPA
├── docker/         # Service-specific Docker configs
├── infrastructure/ # Terraform, Ansible, GitHub Actions
├── prompts/        # LLM prompt files (mirrored in docs/AI_PROMPTS.md)
├── configs/        # YAML runtime configuration
└── logs/           # Runtime logs (gitignored)
```

Full folder map: [docs/LLD.md § Folder Structure](docs/LLD.md#1-folder-structure).

## Governance Rules for AI Agents (Cursor)

Before writing any code, Cursor must act as **Lead Software Architect** and verify:

- Does HLD allow this?
- Does LLD define this?
- Does this violate folder structure?
- Does this require updating README, HLD, LLD, API_SPEC, Docker, or env vars?

See `.cursor/rules/` for enforced rules.

## Contributing

See [docs/CODING_GUIDELINES.md](docs/CODING_GUIDELINES.md). Every feature change must update documentation first.

## License

MIT — see [LICENSE](LICENSE).
