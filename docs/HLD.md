# High-Level Design (HLD) — AI Job Agent

**Version**: 0.2.0  
**Last Updated**: 2026-07-10  
**Status**: Blueprint — No implementation yet

> **Layer rules**: Every folder has one responsibility. See [LAYER_RESPONSIBILITIES.md](LAYER_RESPONSIBILITIES.md).

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Goals & Non-Goals](#2-goals--non-goals)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Components & Services](#5-components--services)
6. [Event Flow](#6-event-flow)
7. [Pipelines](#7-pipelines)
8. [Celery Workers](#8-celery-workers)
9. [Scheduler (Cron Jobs)](#9-scheduler-cron-jobs)
10. [AI Layer](#10-ai-layer)
11. [ATS Layer](#11-ats-layer)
12. [Analytics Layer](#12-analytics-layer)
13. [Database Design Overview](#13-database-design-overview)
14. [Queue Design](#14-queue-design)
15. [Deployment Topology](#15-deployment-topology)
16. [Security Overview](#16-security-overview)
17. [Cross-Cutting Concerns](#17-cross-cutting-concerns)

---

## 1. Product Vision

AI Job Agent automates the full job search lifecycle: resume understanding → job discovery → intelligent matching → resume optimization → ATS application → recruiter outreach → analytics. See [PROJECT_VISION.md](PROJECT_VISION.md) for full vision.

## 2. Goals & Non-Goals

### Goals

| ID | Goal |
|----|------|
| G1 | End-to-end job search automation pipeline |
| G2 | Local-first AI via Ollama (privacy) |
| G3 | Multi-source job discovery (8+ collectors) |
| G4 | Explainable AI matching with scores |
| G5 | Playwright-based ATS auto-apply |
| G6 | Self-hosted via Docker Compose |
| G7 | Documentation-governed development |

### Non-Goals (v1)

- Multi-tenant SaaS
- Mobile native apps
- Interview coaching
- Paid job APIs
- Cloud-only AI (OpenAI/Anthropic as default)

---

## 3. Technology Stack

Every technology choice is deliberate. No technology may be added without updating this section and LLD.md.

| Tool | Purpose | Why This Choice |
|------|---------|-----------------|
| **FastAPI** | Backend REST APIs | Async-native, auto OpenAPI docs, Pydantic integration, high performance |
| **MongoDB** | Primary datastore | Flexible schema for varied resume/job structures; embedding storage; horizontal scaling |
| **Beanie ODM** | Async MongoDB models | Native async with FastAPI; Pydantic-based documents; migration support |
| **React** | Frontend SPA | Component ecosystem, large talent pool, Vite integration |
| **Tailwind CSS** | UI styling | Utility-first, rapid prototyping, consistent design system |
| **TypeScript** | Frontend type safety | Catch errors at compile time; shared types with API contracts |
| **Celery** | Background workers | Battle-tested task queue; retry, routing, monitoring |
| **Redis** | Queue broker + cache | Celery broker; session cache; rate limit counters |
| **APScheduler** | Cron scheduling | Lightweight; integrates with FastAPI lifespan; configurable cron |
| **Playwright** | Browser automation | Multi-browser; reliable selectors; screenshot capture for audit |
| **Ollama** | Local AI inference | Privacy-first; no API costs; runs in Docker; model flexibility |
| **Docker** | Containerization | Reproducible environments; service isolation |
| **Docker Compose** | Local orchestration | Single-command dev stack; production-like locally |
| **Nginx** | Reverse proxy | SSL termination; static file serving; upstream load balancing |
| **GitHub Actions** | CI/CD | Lint, test, build, deploy pipeline |
| **PyMuPDF** | Resume parsing (primary) | Fast PDF text extraction; layout preservation |
| **pdfplumber** | ATS parsing fallback | Table extraction; fallback when PyMuPDF fails |
| **JWT** | Authentication | Stateless auth; refresh token rotation |
| **SMTP/Gmail API** | Email sending | Recruiter outreach; notifications; password reset |
| **Pydantic** | Validation | Request/response schemas; settings management |
| **Loguru** | Structured logging | JSON logs; rotation; Celery integration |
| **Prometheus** (optional) | Metrics | Request latency, queue depth, worker throughput |
| **Grafana** (optional) | Monitoring | Dashboards for Prometheus metrics |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Browser)                                 │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NGINX (Reverse Proxy)                               │
│                    :80 → frontend:5173 / api:8000                         │
└───────────────┬─────────────────────────────────────┬─────────────────────┘
                │                                     │
                ▼                                     ▼
┌───────────────────────────┐         ┌───────────────────────────────────────┐
│   FRONTEND (React/Vite)   │         │         BACKEND (FastAPI)             │
│                           │         │                                       │
│  Pages / Components       │         │  API Layer (v1 routers)               │
│  State (Zustand)          │◄───────►│  Service Layer (business logic)      │
│  API Client (axios)       │  REST   │  Repository Layer (data access)      │
│  Routes                   │         │  Core (auth, jwt, exceptions)        │
└───────────────────────────┘         └───────┬───────────────┬───────────────┘
                                              │               │
                              ┌───────────────┘               └───────────────┐
                              ▼                                               ▼
              ┌───────────────────────────┐               ┌───────────────────────────┐
              │     MongoDB               │               │     Redis                  │
              │                           │               │                            │
              │  users, resumes, jobs,    │               │  Celery broker             │
              │  applications, analytics, │               │  Cache, rate limits        │
              │  embeddings, notifications│               │                            │
              └───────────────────────────┘               └─────────────┬─────────────┘
                                                                        │
                                                                        ▼
                                                        ┌───────────────────────────────┐
                                                        │     CELERY WORKERS            │
                                                        │                               │
                                                        │  resume_parser_worker         │
                                                        │  job_scraper_worker           │
                                                        │  job_match_worker             │
                                                        │  cover_letter_worker          │
                                                        │  resume_optimizer_worker      │
                                                        │  ats_apply_worker             │
                                                        │  analytics_worker             │
                                                        │  notification_worker          │
                                                        │  cleanup_worker               │
                                                        └───────┬───────────┬───────────┘
                                                                │           │
                                                    ┌───────────┘           └───────────┐
                                                    ▼                                   ▼
                                    ┌───────────────────────────┐   ┌───────────────────────┐
                                    │     Ollama (Local LLM)    │   │  Playwright (Browser) │
                                    │                           │   │                       │
                                    │  llama3.2 (generation)   │   │  ATS form automation  │
                                    │  nomic-embed-text (embed) │   │  Screenshot capture   │
                                    └───────────────────────────┘   └───────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCHEDULER (APScheduler / Celery Beat)               │
│                                                                             │
│  Collect Jobs (1h) │ Match Jobs (30m) │ Optimize (daily) │ Analytics (1h) │
│  Cleanup (weekly)  │ Health Check (5m)                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         JOB COLLECTORS (Pluggable)                          │
│                                                                             │
│  Greenhouse │ Lever │ Ashby │ Company Sites │ LinkedIn │ Indeed │         │
│  Naukri │ Wellfound                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Components & Services

### 5.1 API Layer (`backend/app/api/v1/`)

HTTP-only. No business logic. Validates input, calls service, returns response.

| Router | Responsibility |
|--------|---------------|
| `auth/` | Register, login, refresh, password reset |
| `users/` | Profile CRUD |
| `resumes/` | Upload, list, get, update parsed resume |
| `jobs/` | List, search, get job detail |
| `applications/` | Create, update status, list applications |
| `recruiters/` | List, discover, send outreach |
| `analytics/` | Dashboard metrics, funnel data |
| `dashboard/` | Aggregated dashboard endpoint |
| `scheduler/` | View/manage cron schedules |
| `notifications/` | List, mark read |
| `settings/` | User preferences, automation config |
| `health/` | Liveness, readiness probes |

### 5.2 Service Layer (`backend/app/services/`)

All business logic lives here. Services call repositories and enqueue Celery tasks.

| Service | Responsibility |
|---------|---------------|
| `auth/` | Registration, login, token management |
| `resume/` | Upload handling, parse orchestration, embedding trigger |
| `jobs/` | Job search, dedup, collector orchestration |
| `ats/` | Playwright apply orchestration, form mapping |
| `recruiter/` | Recruiter discovery, email orchestration |
| `email/` | SMTP sending, template rendering |
| `analytics/` | Metric aggregation, funnel computation |
| `notifications/` | Notification creation, delivery routing |
| `scheduler/` | Cron job registration, schedule management |

### 5.3 Repository Layer (`backend/app/repositories/`)

Data access only. No business logic. One repository per aggregate root.

| Repository | Collection(s) |
|------------|--------------|
| `UserRepository` | `users` |
| `ResumeRepository` | `resumes`, `parsed_resumes` |
| `JobRepository` | `jobs` |
| `ApplicationRepository` | `applications` |
| `RecruiterRepository` | `recruiters` |
| `AnalyticsRepository` | `analytics` |
| `NotificationRepository` | `notifications` |
| `SettingsRepository` | `settings` |

### 5.4 Collector Layer (`backend/app/collectors/`)

Pluggable job source collectors. Each implements `BaseCollector` interface.

| Collector | Source | Method |
|-----------|--------|--------|
| `greenhouse/` | Greenhouse ATS boards | API + HTML scrape |
| `lever/` | Lever ATS boards | API + HTML scrape |
| `ashby/` | Ashby ATS boards | API + HTML scrape |
| `company_sites/` | Custom career pages | Configurable selectors |
| `linkedin/` | LinkedIn public listings | HTML scrape (rate-limited) |
| `naukri/` | Naukri.com | HTML scrape |
| `indeed/` | Indeed.com | HTML scrape |
| `wellfound/` | Wellfound (AngelList) | HTML scrape |

### 5.5 AI Layer (`backend/app/ai/`)

All LLM interactions isolated here. No direct Ollama calls outside this layer.

| Module | Responsibility |
|--------|---------------|
| `ollama/` | Ollama client wrapper, model management |
| `embeddings/` | Text → vector embedding |
| `prompts/` | Prompt template loader |
| `resume_matching/` | Score resume vs job description |
| `cover_letter/` | Generate cover letter |
| `recruiter_email/` | Generate outreach email |
| `interview/` | Interview Q&A (v2) |

### 5.6 Worker Layer (`backend/app/workers/`)

Celery task definitions. Workers call services/AI layer.

### 5.7 Scheduler Layer (`backend/app/scheduler/`)

APScheduler + Celery Beat cron definitions.

---

## 6. Event Flow

### 6.1 Event-Driven Architecture

Services **never** call workers directly. They publish events via `backend/app/events/`. Workers react. This enables SaaS-scale decoupling.

```
User Action / Scheduler Cron
        │
        ▼
   API / Scheduler (trigger only)
        │
        ▼
   Service (validate, persist via repository)
        │
        ▼
   events/*.publish()  ──NOT── service → service chains
        │
        ▼
   Celery Queue (Redis)
        │
        ▼
   Worker (async only)
        │
        ├── ai/ (model calls, no DB)
        ├── collectors/ (scrape only, no DB)
        ├── repositories/ (persist results)
        └── events/*.publish() (downstream)
```

### 6.2 Event Module (`backend/app/events/`)

| Event File | Publisher | Worker Consumer |
|------------|-----------|-------------------|
| `resume_uploaded.py` | `ResumeService.upload()` | `resume_parser` |
| `jobs_collected.py` | `job_scraper` worker | `job_matcher` |
| `job_matched.py` | `job_matcher` worker | `notification` |
| `application_submitted.py` | `ApplicationService.apply()` | `ats_apply` |
| `email_sent.py` | `recruiter_email` worker | `analytics`, `notification` |

### 6.3 Domain Events (Extended)

| Event | Publisher | Consumer(s) |
|-------|-----------|-------------|
| `resume_uploaded` | ResumeService | `resume_parser` |
| `resume_parsed` | `resume_parser` | `job_matcher` (re-score) |
| `jobs_collected` | `job_scraper` | `job_matcher` |
| `job_matched` | `job_matcher` | `notification` |
| `application_submitted` | ApplicationService / scheduler | `ats_apply` |
| `application_applied` | `ats_apply` | `analytics`, `notification` |
| `email_sent` | `recruiter_email` | `analytics`, `notification` |

---

## 7. Pipelines

### 7.1 User Registration Pipeline

```
POST /auth/register
  → AuthService.register()
  → UserRepository.create()
  → JWT issued
  → Default Settings created
  → Response: { access_token, refresh_token, user }
```

### 7.2 Resume Upload Pipeline

```
POST /resumes/upload (multipart)
  → ResumeService.upload()
  → File saved to UPLOAD_DIR
  → ResumeRepository.create() (status: pending)
  → events.resume_uploaded.publish(resume_id, user_id)
  → Response: { resume_id, status: "processing" }
```

### 7.3 Resume Parsing Pipeline

```
resume_parser_worker(resume_id)
  → Load file from UPLOAD_DIR
  → PyMuPDF extract text (fallback: pdfplumber)
  → AI: extract structured fields (name, skills, experience, education)
  → ParsedResume document created
  → Resume status → "parsed"
  → Publish: resume.parsed → ai_worker (embed task)
```

### 7.4 Embedding Pipeline

```
ai_worker.generate_embedding(resume_id)
  → Load parsed resume text
  → Ollama: nomic-embed-text → vector[768]
  → Store embedding in ParsedResume.embedding
  → Publish: resume.embedded
```

### 7.5 Job Discovery Pipeline

```
Scheduler: collect_jobs (every 1 hour)
  → For each enabled collector in configs/job_sources.yaml:
      → Collector.collect() → raw jobs
      → JobService.deduplicate_and_store()
  → Publish: jobs.collected → job_match_worker
```

### 7.6 AI Matching Pipeline

```
Scheduler: match_jobs (every 30 minutes)
  OR trigger: jobs.collected / resume.embedded
  → job_match_worker:
      → For each user with parsed resume:
          → Embedding similarity: top 50 jobs
          → LLM scoring: detailed 0-100 score per job
          → Store match results in applications (status: "matched")
  → Publish: jobs.matched → notification_worker (if score > threshold)
```

### 7.7 Resume Selection Pipeline

```
User selects job match → chooses resume version
  OR auto-select: highest-scoring resume variant
  → ApplicationService.select_resume(application_id, resume_id)
  → If auto-mode: trigger resume_optimizer_worker
```

### 7.8 ATS Apply Pipeline

```
User approves OR scheduler (9 AM daily)
  → ApplicationService.apply()
  → Generate optimized resume (via resume_optimizer event if needed)
  → ApplicationRepository.update(status: "applying")
  → ApplicationHistoryRepository.log()
  → events.application_submitted.publish(application_id)
  → ats_apply worker:
      → Playwright fill + submit
      → Screenshot captured
      → ApplicationRepository.update(status: "applied")
      → events.application_applied.publish()
```

### 7.9 Recruiter Discovery Pipeline

```
Post-application OR manual trigger
  → RecruiterService.discover(job_id)
  → Scrape job page / LinkedIn for recruiter info
  → Recruiter document created
  → Celery: email_worker.delay(recruiter_id, application_id)
```

### 7.10 Email Generation Pipeline

```
email_worker(recruiter_id, application_id)
  → AI: generate personalized outreach email
  → EmailService.send_via_smtp()
  → Application updated with email status
  → Publish: email.sent
```

### 7.11 Analytics Pipeline

```
Scheduler: analytics (hourly)
  → analytics_worker:
      → Aggregate: applications/week, match distribution, funnel
      → Store in analytics collection
  → Dashboard reads on next request
```

### 7.12 Notification Pipeline

```
Any domain event (jobs.matched, application.submitted, etc.)
  → notification_worker:
      → Create notification document
      → If email enabled: send via EmailService
      → Frontend polls /notifications or WebSocket (v2)
```

---

## 8. Celery Workers

Workers are **background-only**. One worker per concern. Scale independently for SaaS.

| Worker | File | Queue | Tasks | Concurrency |
|--------|------|-------|-------|-------------|
| `resume_parser` | `resume_parser.py` | `resume` | `parse_resume` | 2 |
| `job_scraper` | `job_scraper.py` | `scraping` | `collect_jobs` | 1 |
| `job_matcher` | `job_matcher.py` | `matching` | `score_all`, `score_user` | 2 |
| `resume_optimizer` | `resume_optimizer.py` | `ai` | `optimize_resume` | 2 |
| `cover_letter` | `cover_letter.py` | `ai` | `generate_cover_letter` | 2 |
| `ats_apply` | `ats_apply.py` | `ats` | `apply_to_job`, `process_queue` | 3 |
| `recruiter_email` | `recruiter_email.py` | `email` | `send_email`, `process_queue` | 2 |
| `analytics` | `analytics.py` | `analytics` | `aggregate`, `record_event` | 1 |
| `notification` | `notification.py` | `notifications` | `notify_match`, `notify_application` | 4 |
| `cleanup` | `cleanup.py` | `maintenance` | `run`, `health_check` | 1 |

### Queue Configuration

| Queue | Routing Key | Worker | Priority |
|-------|-------------|--------|----------|
| `resume` | `resume.*` | `resume_parser` | High |
| `scraping` | `scraping.*` | `job_scraper` | Low |
| `matching` | `matching.*` | `job_matcher` | Medium |
| `ai` | `ai.*` | `resume_optimizer`, `cover_letter` | Medium |
| `ats` | `ats.*` | `ats_apply` | High |
| `email` | `email.*` | `recruiter_email` | Medium |
| `analytics` | `analytics.*` | `analytics` | Low |
| `notifications` | `notifications.*` | `notification` | High |
| `maintenance` | `maintenance.*` | `cleanup` | Lowest |

---

## 9. Scheduler (Cron Jobs)

`scheduler/` **only triggers workers**. No scraping, AI, or business logic. Config: `configs/scheduler.yaml`.

| Job | Schedule | Triggers | Description |
|-----|----------|----------|-------------|
| Collect Jobs | Every 1 hour | `job_scraper.collect_jobs` | Run all enabled collectors |
| Score Jobs | Every 30 minutes | `job_matcher.score_all` | AI match for all users |
| ATS Apply | Daily 9:00 AM UTC | `ats_apply.process_queue` | Process approved applications |
| Recruiter Email | Daily 10:00 AM UTC | `recruiter_email.process_queue` | Send queued outreach emails |
| Analytics | Every 1 hour | `analytics.aggregate` | Compute dashboard metrics |
| Cleanup | Sunday 3:00 AM UTC | `cleanup.run` | Purge old jobs, logs, temp files |
| Health Check | Every 5 minutes | `cleanup.health_check` | Verify MongoDB, Redis, Ollama |

---

## 10. AI Layer

### Model Configuration (`configs/ai.yaml`)

```yaml
ollama:
  base_url: "${OLLAMA_BASE_URL}"
  models:
    generation: "llama3.2"
    embedding: "nomic-embed-text"
  timeout_seconds: 120
  max_tokens: 4096

matching:
  similarity_threshold: 0.65
  llm_score_weight: 0.6
  embedding_score_weight: 0.4
  max_jobs_per_batch: 50

optimization:
  max_keywords_to_add: 15
  preserve_original_structure: true
```

### AI Operations

| Operation | Model | Input | Output |
|-----------|-------|-------|--------|
| Resume field extraction | llama3.2 | Raw resume text | Structured JSON |
| Embedding | nomic-embed-text | Resume/job text | float[768] |
| Match scoring | llama3.2 | Resume + JD | Score 0-100 + explanation |
| Cover letter | llama3.2 | Resume + JD + company | Cover letter text |
| Recruiter email | llama3.2 | Resume + JD + recruiter | Email subject + body |
| Resume optimization | llama3.2 | Resume + JD | Optimized resume text |
| ATS keyword analysis | llama3.2 | Resume + JD | Missing keywords list |

---

## 11. ATS Layer

### Playwright Automation Strategy

1. **Selector Registry**: Per-ATS selectors stored in `configs/companies.yaml`
2. **Generic Fallback**: Common patterns (input[name=email], input[type=file])
3. **Screenshot Audit**: Every apply attempt captures before/after screenshots
4. **Retry Policy**: 3 retries with exponential backoff
5. **Concurrency Limit**: Max 3 parallel browser contexts

### Supported ATS Platforms (v1)

| ATS | Detection | Apply Method |
|-----|-----------|-------------|
| Greenhouse | URL pattern `/greenhouse.io/` | Form fill + file upload |
| Lever | URL pattern `/jobs.lever.co/` | Form fill + file upload |
| Ashby | URL pattern `/ashbyhq.com/` | Form fill + file upload |
| Workday | URL pattern `/myworkdayjobs.com/` | Multi-step form (v2) |
| Generic | Fallback | Best-effort form detection |

---

## 12. Analytics Layer

### Metrics Tracked

| Metric | Granularity | Storage |
|--------|-------------|---------|
| Jobs discovered | Daily | `analytics.daily_jobs` |
| Matches created | Daily | `analytics.daily_matches` |
| Applications submitted | Daily | `analytics.daily_applications` |
| Response rate | Weekly | `analytics.weekly_response_rate` |
| Match score distribution | Daily | `analytics.score_histogram` |
| Source breakdown | Daily | `analytics.source_counts` |
| Pipeline funnel | Daily | `analytics.funnel` |

### Funnel Stages

```
Discovered → Matched → Selected → Optimized → Applied → Response
```

---

## 13. Database Design Overview

MongoDB with Beanie ODM. **18 collections**. Full schema in [DATABASE.md](DATABASE.md). Access **only** via `repositories/`.

| Collection | Purpose |
|------------|---------|
| `users` | Auth credentials |
| `sessions` | Refresh tokens / active sessions |
| `profiles` | User profile (name, bio, links) |
| `resumes` | Resume file metadata |
| `parsed_resumes` | Structured resume + embeddings |
| `jobs` | Discovered listings (90-day TTL) |
| `companies` | Company metadata |
| `applications` | Application state + match scores |
| `application_history` | Immutable status audit trail |
| `recruiters` | Recruiter contacts |
| `emails` | Sent/draft emails |
| `notifications` | In-app notifications |
| `analytics` | Aggregated metrics |
| `scheduler_logs` | Cron execution logs |
| `ai_logs` | LLM request/response logs |
| `prompt_logs` | Prompt version + output logs |
| `settings` | Automation preferences |
| `audit_logs` | Security compliance audit |

---

## 14. Queue Design

```
Redis (broker)
  ├── resume          → resume_parser
  ├── scraping        → job_scraper
  ├── matching        → job_matcher
  ├── ai              → resume_optimizer, cover_letter
  ├── ats             → ats_apply
  ├── email           → recruiter_email
  ├── analytics       → analytics
  ├── notifications   → notification
  └── maintenance     → cleanup
```

**Retry Policy**: All tasks retry 3 times with exponential backoff (60s, 300s, 900s). Failed tasks logged to `scheduler_logs` collection.

**Dead Letter**: After 3 failures, task moved to `maintenance` queue for manual review.

---

## 15. Deployment Topology

### Local Development (Docker Compose)

```
Services:
  nginx          → :80
  frontend       → :5173 (dev) / static (prod)
  api            → :8000
  celery-worker  → (4 workers: resume, scraping, ai+matching, ats+notifications)
  celery-beat    → scheduler
  mongodb        → :27017
  redis          → :6379
  ollama         → :11434
```

### Production (Single EC2)

```
EC2 (t3.xlarge or larger)
  ├── Docker Compose (same as local, production env)
  ├── Nginx with SSL (Let's Encrypt)
  ├── MongoDB (container, volume-mounted)
  ├── Redis (container)
  ├── Ollama (container, GPU optional)
  └── Volumes: mongo-data, uploads, logs, playwright-data
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full details.

---

## 16. Security Overview

- JWT access tokens (30 min) + refresh tokens (7 days)
- Passwords hashed with bcrypt
- All API endpoints require auth except `/health` and `/auth/*`
- Rate limiting via Redis (60 req/min per user)
- Resume files stored with user-scoped paths
- No resume data sent to external APIs (Ollama local)
- CORS restricted to configured origins
- See [SECURITY.md](SECURITY.md) for full spec

---

## 17. Cross-Cutting Concerns

### Logging

Loguru JSON format. Every service logs: `request_id`, `user_id`, `action`, `duration_ms`.

### Error Handling

Custom exceptions in `core/exceptions.py`. API returns consistent error envelope:

```json
{
  "error": {
    "code": "RESUME_PARSE_FAILED",
    "message": "Unable to parse resume",
    "details": {}
  }
}
```

### Configuration

Layered configuration with a single source of truth for secrets and environment-specific values:

```
.env (gitignored)
  └── app/config.py (Pydantic Settings — typed fields only, no hardcoded secrets)
        └── services / workers / API (read via get_settings())
```

#### Configuration Layer

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Secrets & env | Root `.env` | MongoDB URI, JWT keys, SMTP, Redis, API URLs |
| Typed access | `backend/app/config.py` | Validate, parse, and expose `Settings` |
| Non-secret runtime | `configs/*.yaml` | Scheduler, collectors, AI weights (future) |

Services and workers **must not** read `os.environ` directly. All configuration flows through `get_settings()`.

#### Secrets Management

- **Never** commit `.env` or embed credentials in Python source files.
- `.env.example` documents every variable with safe placeholders.
- Production (`APP_ENV=production`) enforces strong `APP_SECRET_KEY` and `JWT_SECRET_KEY` (32+ characters, no placeholder values).
- Missing required variables cause startup failure with a clear Pydantic validation error.

#### Storage Architecture

Files are stored on disk under `STORAGE_ROOT` with per-type subdirectories:

| Setting | Default subdir | Purpose |
|---------|----------------|---------|
| `RESUME_STORAGE_DIR` | `resumes` | Uploaded resume PDFs |
| `GENERATED_RESUME_DIR` | `generated-resumes` | AI-optimized resumes |
| `COVER_LETTER_DIR` | `cover-letters` | Generated cover letters |
| `PROFILE_IMAGE_DIR` | `profile-images` | User avatars |
| `TEMP_DIR` | `temp` | Transient processing files |

**MongoDB stores relative paths only** (e.g. `userId/uuid.pdf`). Public URLs are built at API response time from `API_BASE_URL` — never persisted in the database.

`STORAGE_PROVIDER=local` today; S3-compatible providers are reserved for a future phase.

#### Environment Variables

See `.env.example` and [LLD.md §20](LLD.md#20-environment-variables). Key groups:

| Group | Examples | Required |
|-------|----------|----------|
| Application | `APP_ENV`, `APP_DEBUG`, `API_BASE_URL`, `CORS_ORIGINS` | Yes |
| Database | `MONGODB_URI`, `MONGODB_DB_NAME` | Yes |
| Auth | `JWT_SECRET_KEY`, `APP_SECRET_KEY` | Yes |
| Infrastructure | `REDIS_URL`, `CELERY_BROKER_URL`, `OLLAMA_BASE_URL` | Yes |
| Storage | `STORAGE_ROOT`, `RESUME_STORAGE_DIR`, … | Yes |
| Email | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | Optional |
| Frontend | `FRONTEND_BASE_URL`, `VITE_API_BASE_URL` | Yes (frontend) |

**Development:** `APP_ENV=development`, localhost URLs, optional SMTP (links logged to console).

**Production:** `APP_ENV=production`, strong secrets, production hostnames in `API_BASE_URL` and `CORS_ORIGINS`.

### Health Checks

| Endpoint | Checks |
|----------|--------|
| `GET /health/live` | API process alive |
| `GET /health/ready` | MongoDB + Redis + Ollama reachable |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial HLD from Engineering Blueprint |
| 0.2.0 | 2026-07-10 | SRP layers, events module, 18 collections, worker rename, scheduler update |
| 0.3.0 | 2026-07-11 | Configuration layer: secrets in `.env` only, storage path architecture |
