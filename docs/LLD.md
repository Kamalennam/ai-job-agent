# Low-Level Design (LLD) — AI Job Agent

**Version**: 0.2.0  
**Last Updated**: 2026-07-10  
**Status**: Blueprint — No implementation yet

> This document is the **implementation contract**. See [LAYER_RESPONSIBILITIES.md](LAYER_RESPONSIBILITIES.md) for strict folder rules.

---

## Table of Contents

1. [Folder Structure](#1-folder-structure)
2. [Backend Modules](#2-backend-modules)
3. [API Endpoints](#3-api-endpoints)
4. [DTOs / Schemas](#4-dtos--schemas)
5. [MongoDB Collections](#5-mongodb-collections)
6. [Repositories](#6-repositories)
7. [Services](#7-services)
8. [Celery Workers & Tasks](#8-celery-workers--tasks)
9. [Celery Queues](#9-celery-queues)
10. [Scheduler / Cron Jobs](#10-scheduler--cron-jobs)
11. [AI Prompts](#11-ai-prompts)
12. [Job Collectors](#12-job-collectors)
13. [Domain Events](#13-domain-events)
14. [Docker Containers](#14-docker-containers)
15. [Frontend Pages](#15-frontend-pages)
16. [Frontend Components](#16-frontend-components)
17. [Frontend Routes](#17-frontend-routes)
18. [Frontend Services & State](#18-frontend-services--state)
19. [Configuration Files](#19-configuration-files)
20. [Environment Variables](#20-environment-variables)

---

## 1. Folder Structure

Every folder listed below is **immutable in name**. No folder may be renamed, moved, or created outside this tree without updating this document and HLD.md.

```
AI-Job-Agent/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── package.json
│
├── docs/                          # Engineering Blueprint (this directory)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── app/
│       ├── main.py                # FastAPI app factory, router registration
│       ├── lifespan.py            # Startup/shutdown: DB, Redis, scheduler
│       ├── config.py              # Pydantic Settings (env + yaml)
│       ├── constants.py           # Enums, queue names, status codes
│       │
│       ├── api/v1/                # HTTP routers ONLY — no business logic
│       │   ├── auth/
│       │   ├── users/
│       │   ├── resumes/
│       │   ├── jobs/
│       │   ├── applications/
│       │   ├── recruiters/
│       │   ├── analytics/
│       │   ├── dashboard/
│       │   ├── scheduler/
│       │   ├── notifications/
│       │   ├── settings/
│       │   └── health/
│       │
│       ├── core/                  # Cross-cutting infrastructure
│       │   ├── auth.py            # get_current_user dependency
│       │   ├── jwt.py             # Token create/verify/decode
│       │   ├── security.py        # Password hash, bcrypt
│       │   ├── logger.py          # Loguru setup
│       │   ├── exceptions.py      # Custom HTTP exceptions
│       │   └── dependencies.py    # Shared FastAPI dependencies
│       │
│       ├── db/
│       │   ├── client.py          # Motor/Beanie init
│       │   ├── init_db.py         # Collection/index setup
│       │   ├── migrations/
│       │   └── seed/
│       │
│       ├── models/                # Beanie Document models (DB layer)
│       ├── schemas/               # Pydantic request/response DTOs
│       ├── repositories/          # MongoDB ONLY — 18 repositories
│       ├── services/              # Business logic — publishes events, never workers
│       ├── events/                # Event publishers → queue workers
│       │   ├── resume_uploaded.py
│       │   ├── jobs_collected.py
│       │   ├── job_matched.py
│       │   ├── application_submitted.py
│       │   └── email_sent.py
│       ├── collectors/            # Job collection ONLY
│       ├── ai/                    # AI ONLY — no DB, no APIs
│       ├── workers/               # Background Celery tasks ONLY
│       │   ├── resume_parser.py
│       │   ├── job_scraper.py
│       │   ├── job_matcher.py
│       │   ├── resume_optimizer.py
│       │   ├── cover_letter.py
│       │   ├── ats_apply.py
│       │   ├── recruiter_email.py
│       │   ├── analytics.py
│       │   ├── notification.py
│       │   └── cleanup.py
│       ├── scheduler/             # Cron triggers ONLY — no scraping logic
│       ├── utils/
│       ├── templates/             # Email HTML templates
│       ├── static/
│       └── tests/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── app/                   # App root, providers
│       ├── assets/
│       ├── components/          # Reusable UI components
│       ├── layouts/               # Page layouts
│       ├── pages/                 # Route-level page components
│       ├── hooks/                 # Custom React hooks
│       ├── services/              # API client functions
│       ├── store/                 # Zustand state stores
│       ├── types/                 # TypeScript interfaces
│       ├── utils/
│       ├── routes/                # Route definitions
│       ├── styles/
│       └── main.tsx
│
├── docker/                        # Per-service Docker configs
├── infrastructure/                # IaC and CI/CD
├── prompts/                       # LLM prompt markdown files
├── configs/                       # Runtime YAML configuration
└── logs/                          # Runtime logs (gitignored)
```

---

## 2. Backend Modules

### 2.1 `app/main.py`

| Responsibility | Detail |
|---------------|--------|
| Create FastAPI app | Title, version, docs URL |
| Register routers | All `api/v1/*` routers with prefix `/api/v1` |
| CORS middleware | Origins from `CORS_ORIGINS` env |
| Exception handlers | Map custom exceptions to HTTP responses |
| Lifespan | Delegate to `lifespan.py` |

### 2.2 `app/lifespan.py`

| Phase | Actions |
|-------|---------|
| Startup | Connect MongoDB (Beanie init), verify Redis, start APScheduler, load configs |
| Shutdown | Stop scheduler, close MongoDB connection, close Redis |

### 2.3 `app/config.py`

Pydantic `BaseSettings` class `Settings` — **typed fields only; no hardcoded secrets**.

#### Settings class

| Field group | Fields | Notes |
|-------------|--------|-------|
| Application | `app_name`, `app_env`, `app_debug`, `app_secret_key`, `api_v1_prefix`, `api_base_url`, `cors_origins` | `app_env`: `development` \| `production` \| `testing` |
| MongoDB | `mongodb_uri`, `mongodb_db_name` | Required |
| Redis / Celery | `redis_url`, `celery_broker_url`, `celery_result_backend` | Required |
| JWT | `jwt_secret_key`, `jwt_algorithm`, `jwt_access_token_expire_minutes`, `jwt_refresh_token_expire_days` | Required secret |
| Ollama | `ollama_base_url`, `ollama_model`, `ollama_embedding_model`, `prompts_dir`, `configs_dir` | Required URLs/models |
| Frontend | `frontend_base_url` | Verification links |
| Email | `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `smtp_from_email`, `email_verification_expire_hours` | SMTP optional |
| Storage | `storage_provider`, `storage_root`, `resume_storage_dir`, `generated_resume_dir`, `cover_letter_dir`, `profile_image_dir`, `temp_dir` | Relative paths in DB |
| Upload limits | `max_resume_size_mb`, `allowed_resume_extensions` | Resume validation |

#### Configuration flow

```
.env (repo root)
  → pydantic-settings loads on Settings() instantiation
  → get_settings() (@lru_cache singleton)
  → injected implicitly by services via get_settings()
```

Startup fails with a Pydantic `ValidationError` if any required field is missing.

#### Environment loading

- Primary env file: repository root `.env`
- Fallback: process environment (Docker Compose `env_file`, CI secrets)
- Case-insensitive env keys (`MONGODB_URI` → `mongodb_uri`)
- Production validator rejects weak `app_secret_key` / `jwt_secret_key`

#### Storage configuration

| Property | Resolves to |
|----------|-------------|
| `resolved_storage_root` | Absolute `STORAGE_ROOT` |
| `resolved_resume_storage_dir` | `{storage_root}/{resume_storage_dir}` |
| `resolved_generated_resume_dir` | `{storage_root}/{generated_resume_dir}` |
| `resolved_cover_letter_dir` | `{storage_root}/{cover_letter_dir}` |
| `resolved_profile_image_dir` | `{storage_root}/{profile_image_dir}` |
| `resolved_temp_dir` | `{storage_root}/{temp_dir}` |
| `build_resume_public_url(path)` | `{api_base_url}/storage/resumes/{path}` |

MongoDB `resumes.file_path` stores the relative path. `file_url` stores the full public URL at upload time (S3-style). API responses return the stored `file_url`, or compute from `file_path` when missing (legacy records).

Nested YAML loaders for `configs/*.yaml` are planned for non-secret runtime config.

### 2.4 `app/constants.py`

```python
# Enums and constants — no magic strings in codebase
class ApplicationStatus(str, Enum):
    MATCHED = "matched"
    SELECTED = "selected"
    OPTIMIZING = "optimizing"
    READY = "ready"
    APPLYING = "applying"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"

class ResumeStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"

class AutomationMode(str, Enum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"

class QueueName(str, Enum):
    RESUME = "resume"
    SCRAPING = "scraping"
    MATCHING = "matching"
    AI = "ai"
    ATS = "ats"
    EMAIL = "email"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    MAINTENANCE = "maintenance"
```

---

## 3. API Endpoints

All endpoints prefixed with `/api/v1`. Auth required unless noted.

### 3.1 Auth (`api/v1/auth/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| POST | `/auth/register` | No | `RegisterRequest` | `TokenResponse` | `AuthService.register` |
| POST | `/auth/login` | No | `LoginRequest` | `TokenResponse` | `AuthService.login` |
| POST | `/auth/refresh` | No | `RefreshRequest` | `TokenResponse` | `AuthService.refresh` |
| POST | `/auth/forgot-password` | No | `ForgotPasswordRequest` | `MessageResponse` | `AuthService.forgot_password` |
| POST | `/auth/reset-password` | No | `ResetPasswordRequest` | `MessageResponse` | `AuthService.reset_password` |
| POST | `/auth/logout` | Yes | — | `MessageResponse` | `AuthService.logout` |

### 3.2 Users (`api/v1/users/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/users/me` | Yes | — | `UserResponse` | `UserService.get_profile` |
| PUT | `/users/me` | Yes | `UpdateUserRequest` | `UserResponse` | `UserService.update_profile` |
| DELETE | `/users/me` | Yes | — | `MessageResponse` | `UserService.delete_account` |

### 3.3 Resumes (`api/v1/resumes/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| POST | `/resumes/upload` | Yes | multipart file | `ResumeResponse` | `ResumeService.upload` |
| GET | `/resumes` | Yes | — | `ResumeListResponse` | `ResumeService.list_resumes` |
| GET | `/resumes/{id}` | Yes | — | `ResumeDetailResponse` | `ResumeService.get_resume` |
| PUT | `/resumes/{id}` | Yes | `UpdateParsedResumeRequest` | `ParsedResumeResponse` | `ResumeService.update_parsed` |
| DELETE | `/resumes/{id}` | Yes | — | `MessageResponse` | `ResumeService.delete_resume` |
| POST | `/resumes/{id}/reparse` | Yes | — | `ResumeResponse` | `ResumeService.trigger_reparse` |
| GET | `/resumes/{id}/download` | Yes | — | file stream | `ResumeService.download` |

### 3.4 Jobs (`api/v1/jobs/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/jobs` | Yes | query: `JobSearchParams` | `JobListResponse` | `JobService.search_jobs` |
| GET | `/jobs/{id}` | Yes | — | `JobDetailResponse` | `JobService.get_job` |
| POST | `/jobs/collect` | Yes | `CollectJobsRequest` | `MessageResponse` | `JobService.trigger_collection` |
| GET | `/jobs/sources` | Yes | — | `JobSourcesResponse` | `JobService.list_sources` |

### 3.5 Applications (`api/v1/applications/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/applications` | Yes | query: `ApplicationFilterParams` | `ApplicationListResponse` | `ApplicationService.list` |
| GET | `/applications/{id}` | Yes | — | `ApplicationDetailResponse` | `ApplicationService.get` |
| POST | `/applications` | Yes | `CreateApplicationRequest` | `ApplicationResponse` | `ApplicationService.create` |
| PUT | `/applications/{id}/status` | Yes | `UpdateStatusRequest` | `ApplicationResponse` | `ApplicationService.update_status` |
| POST | `/applications/{id}/apply` | Yes | — | `ApplicationResponse` | `ApplicationService.trigger_apply` |
| POST | `/applications/{id}/optimize` | Yes | — | `ApplicationResponse` | `ApplicationService.trigger_optimize` |
| GET | `/applications/{id}/cover-letter` | Yes | — | `CoverLetterResponse` | `ApplicationService.get_cover_letter` |

### 3.6 Recruiters (`api/v1/recruiters/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/recruiters` | Yes | query: filters | `RecruiterListResponse` | `RecruiterService.list` |
| GET | `/recruiters/{id}` | Yes | — | `RecruiterDetailResponse` | `RecruiterService.get` |
| POST | `/recruiters/discover` | Yes | `DiscoverRecruiterRequest` | `RecruiterResponse` | `RecruiterService.discover` |
| POST | `/recruiters/{id}/send-email` | Yes | `SendEmailRequest` | `EmailResponse` | `RecruiterService.send_email` |

### 3.7 Analytics (`api/v1/analytics/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/analytics/overview` | Yes | query: date range | `AnalyticsOverviewResponse` | `AnalyticsService.overview` |
| GET | `/analytics/funnel` | Yes | query: date range | `FunnelResponse` | `AnalyticsService.funnel` |
| GET | `/analytics/sources` | Yes | — | `SourceBreakdownResponse` | `AnalyticsService.sources` |
| GET | `/analytics/scores` | Yes | — | `ScoreDistributionResponse` | `AnalyticsService.scores` |

### 3.8 Dashboard (`api/v1/dashboard/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/dashboard` | Yes | — | `DashboardResponse` | `DashboardService.aggregate` |

### 3.9 Scheduler (`api/v1/scheduler/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/scheduler/jobs` | Yes | — | `SchedulerJobsResponse` | `SchedulerService.list_jobs` |
| GET | `/scheduler/logs` | Yes | query: pagination | `SchedulerLogsResponse` | `SchedulerService.get_logs` |

### 3.10 Notifications (`api/v1/notifications/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/notifications` | Yes | query: pagination | `NotificationListResponse` | `NotificationService.list` |
| PUT | `/notifications/{id}/read` | Yes | — | `NotificationResponse` | `NotificationService.mark_read` |
| PUT | `/notifications/read-all` | Yes | — | `MessageResponse` | `NotificationService.mark_all_read` |

### 3.11 Settings (`api/v1/settings/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/settings` | Yes | — | `SettingsResponse` | `SettingsService.get` |
| PUT | `/settings` | Yes | `UpdateSettingsRequest` | `SettingsResponse` | `SettingsService.update` |

### 3.12 Health (`api/v1/health/`)

| Method | Path | Auth | Request DTO | Response DTO | Service |
|--------|------|------|-------------|--------------|---------|
| GET | `/health/live` | No | — | `HealthResponse` | — |
| GET | `/health/ready` | No | — | `HealthResponse` | checks DB, Redis, Ollama |

---

## 4. DTOs / Schemas

All schemas in `backend/app/schemas/`. Naming: `{Entity}{Action}Request` / `{Entity}Response`.

### 4.1 `schemas/auth.py`

| Schema | Fields |
|--------|--------|
| `RegisterRequest` | email, password, full_name |
| `LoginRequest` | email, password |
| `RefreshRequest` | refresh_token |
| `ForgotPasswordRequest` | email |
| `ResetPasswordRequest` | token, new_password |
| `TokenResponse` | access_token, refresh_token, token_type, expires_in |
| `MessageResponse` | message |

### 4.2 `schemas/resume.py`

| Schema | Fields |
|--------|--------|
| `ResumeResponse` | id, filename, status, created_at |
| `ResumeDetailResponse` | id, filename, status, parsed_resume, created_at |
| `ResumeListResponse` | items: list[ResumeResponse], total |
| `ParsedResumeResponse` | id, name, email, phone, skills, experience, education, summary |
| `UpdateParsedResumeRequest` | name?, email?, phone?, skills?, experience?, education?, summary? |
| `ExperienceDTO` | company, title, start_date, end_date, description |
| `EducationDTO` | institution, degree, field, start_date, end_date |

### 4.3 `schemas/jobs.py`

| Schema | Fields |
|--------|--------|
| `JobSearchParams` | query?, location?, remote?, source?, page, page_size |
| `JobResponse` | id, title, company, location, source, posted_at, apply_url |
| `JobDetailResponse` | id, title, company, location, description, requirements, source, apply_url, posted_at |
| `JobListResponse` | items: list[JobResponse], total, page, page_size |
| `CollectJobsRequest` | sources?: list[str] |
| `JobSourcesResponse` | sources: list[JobSourceDTO] |
| `JobSourceDTO` | name, enabled, last_collected_at, job_count |

### 4.4 `schemas/application.py`

| Schema | Fields |
|--------|--------|
| `CreateApplicationRequest` | job_id, resume_id? |
| `ApplicationResponse` | id, job_id, resume_id, status, match_score, created_at |
| `ApplicationDetailResponse` | id, job, resume, status, match_score, match_explanation, cover_letter, applied_at, screenshot_url |
| `ApplicationListResponse` | items: list[ApplicationResponse], total |
| `ApplicationFilterParams` | status?, min_score?, page, page_size |
| `UpdateStatusRequest` | status |
| `CoverLetterResponse` | content, generated_at |

### 4.5 `schemas/analytics.py`

| Schema | Fields |
|--------|--------|
| `AnalyticsOverviewResponse` | total_jobs, total_matches, total_applications, response_rate |
| `FunnelResponse` | discovered, matched, selected, applied, response |
| `SourceBreakdownResponse` | sources: list[{name, count}] |
| `ScoreDistributionResponse` | buckets: list[{range, count}] |
| `DashboardResponse` | overview, recent_matches, recent_applications, notifications_count |

### 4.6 `schemas/common.py`

| Schema | Fields |
|--------|--------|
| `PaginationParams` | page, page_size |
| `ErrorResponse` | error: { code, message, details } |
| `HealthResponse` | status, checks: dict |

---

## 5. MongoDB Collections

**18 collections**. Full schemas in [DATABASE.md](DATABASE.md). One repository per collection.

| # | Collection | Model File | Repository |
|---|------------|------------|------------|
| 1 | `users` | `user.py` | `UserRepository` |
| 2 | `sessions` | `session.py` | `SessionRepository` |
| 3 | `profiles` | `profile.py` | `ProfileRepository` |
| 4 | `resumes` | `resume.py` | `ResumeRepository` |
| 5 | `parsed_resumes` | `parsed_resume.py` | `ParsedResumeRepository` |
| 6 | `jobs` | `job.py` | `JobRepository` |
| 7 | `companies` | `company.py` | `CompanyRepository` |
| 8 | `applications` | `application.py` | `ApplicationRepository` |
| 9 | `application_history` | `application_history.py` | `ApplicationHistoryRepository` |
| 10 | `recruiters` | `recruiter.py` | `RecruiterRepository` |
| 11 | `emails` | `email.py` | `EmailRepository` |
| 12 | `notifications` | `notification.py` | `NotificationRepository` |
| 13 | `analytics` | `analytics.py` | `AnalyticsRepository` |
| 14 | `scheduler_logs` | `scheduler.py` | `SchedulerLogRepository` |
| 15 | `ai_logs` | `ai_log.py` | `AILogRepository` |
| 16 | `prompt_logs` | `prompt_log.py` | `PromptLogRepository` |
| 17 | `settings` | `settings.py` | `SettingsRepository` |
| 18 | `audit_logs` | `audit_log.py` | `AuditLogRepository` |

### 5.1 `users` (auth only)

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `email` | string | Yes | unique |
| `password_hash` | string | Yes | — |
| `is_active` | bool | Yes | — |
| `created_at` | datetime | Yes | — |
| `updated_at` | datetime | Yes | — |

### 5.2 `sessions`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `refresh_token_hash` | string | Yes | — |
| `expires_at` | datetime | Yes | index |
| `revoked` | bool | Yes | — |
| `created_at` | datetime | Yes | — |

### 5.3 `profiles`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | unique |
| `full_name` | string | Yes | — |
| `headline` | string | No | — |
| `location` | string | No | — |
| `linkedin_url` | string | No | — |
| `avatar_url` | string | No | — |
| `bio` | string | No | — |
| `updated_at` | datetime | Yes | — |

### 5.4 `resumes`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `filename` | string | Yes | — |
| `file_path` | string | Yes | — |
| `file_url` | string | No | — |
| `file_size` | int | Yes | — |
| `mime_type` | string | Yes | — |
| `status` | ResumeStatus | Yes | index |
| `is_primary` | bool | Yes | — |
| `created_at` | datetime | Yes | — |

### 5.5 `parsed_resumes`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `resume_id` | ObjectId | Yes | unique |
| `user_id` | ObjectId | Yes | index |
| `name` | string | No | — |
| `email` | string | No | — |
| `phone` | string | No | — |
| `skills` | list[string] | No | — |
| `experience` | list[Experience] | No | — |
| `education` | list[Education] | No | — |
| `summary` | string | No | — |
| `embedding` | list[float] | No | vector index |
| `raw_text` | string | No | text index |
| `parsed_at` | datetime | Yes | — |

### 5.6 `jobs`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `title` | string | Yes | text |
| `company` | string | Yes | index |
| `location` | string | No | — |
| `description` | string | Yes | text |
| `requirements` | string | No | — |
| `source` | string | Yes | index |
| `source_id` | string | No | unique compound with source |
| `apply_url` | string | Yes | — |
| `salary_min` | int | No | — |
| `salary_max` | int | No | — |
| `remote` | bool | No | index |
| `posted_at` | datetime | No | index |
| `collected_at` | datetime | Yes | TTL index (90 days) |
| `embedding` | list[float] | No | vector index |

### 5.7 `applications`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `job_id` | ObjectId | Yes | index |
| `resume_id` | ObjectId | No | — |
| `status` | ApplicationStatus | Yes | index |
| `match_score` | float | No | index |
| `match_explanation` | string | No | — |
| `cover_letter` | string | No | — |
| `optimized_resume_path` | string | No | — |
| `applied_at` | datetime | No | — |
| `screenshot_path` | string | No | — |
| `created_at` | datetime | Yes | — |
| `updated_at` | datetime | Yes | — |

### 5.8 `application_history`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `application_id` | ObjectId | Yes | index |
| `user_id` | ObjectId | Yes | index |
| `from_status` | ApplicationStatus | No | — |
| `to_status` | ApplicationStatus | Yes | — |
| `actor` | string | Yes | — |
| `metadata` | dict | No | — |
| `created_at` | datetime | Yes | index |

### 5.9 `companies`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `name` | string | Yes | unique |
| `website` | string | No | — |
| `ats_type` | string | No | — |
| `careers_url` | string | No | — |

### 5.10 `recruiters`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `job_id` | ObjectId | Yes | index |
| `name` | string | Yes | — |
| `title` | string | No | — |
| `email` | string | No | — |
| `linkedin_url` | string | No | — |
| `email_sent` | bool | No | — |
| `email_sent_at` | datetime | No | — |

### 5.11 `emails`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `recruiter_id` | ObjectId | No | — |
| `application_id` | ObjectId | No | index |
| `subject` | string | Yes | — |
| `body` | string | Yes | — |
| `status` | EmailStatus | Yes | index |
| `sent_at` | datetime | No | — |
| `created_at` | datetime | Yes | — |

### 5.12 `analytics`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `date` | date | Yes | compound with user_id |
| `jobs_discovered` | int | Yes | — |
| `matches_created` | int | Yes | — |
| `applications_submitted` | int | Yes | — |
| `responses_received` | int | Yes | — |
| `score_histogram` | dict | No | — |
| `source_counts` | dict | No | — |
| `funnel` | dict | No | — |

### 5.13 `notifications`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | index |
| `type` | string | Yes | — |
| `title` | string | Yes | — |
| `message` | string | Yes | — |
| `read` | bool | Yes | index |
| `data` | dict | No | — |
| `created_at` | datetime | Yes | index |

### 5.14 `settings`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | Yes | unique |
| `automation_mode` | AutomationMode | Yes | — |
| `match_threshold` | float | Yes | — |
| `preferred_locations` | list[string] | No | — |
| `preferred_titles` | list[string] | No | — |
| `remote_only` | bool | Yes | — |
| `enabled_sources` | list[string] | Yes | — |
| `email_notifications` | bool | Yes | — |
| `ai_model` | string | Yes | — |

### 5.15 `scheduler_logs`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `job_name` | string | Yes | index |
| `status` | string | Yes | — |
| `started_at` | datetime | Yes | — |
| `completed_at` | datetime | No | — |
| `error` | string | No | — |
| `metadata` | dict | No | — |

### 5.16 `ai_logs`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | No | index |
| `operation` | string | Yes | index |
| `model` | string | Yes | — |
| `duration_ms` | int | Yes | — |
| `success` | bool | Yes | — |
| `created_at` | datetime | Yes | index |

### 5.17 `prompt_logs`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `prompt_name` | string | Yes | index |
| `prompt_version` | string | Yes | — |
| `input_hash` | string | Yes | — |
| `output_preview` | string | Yes | — |
| `model` | string | Yes | — |
| `created_at` | datetime | Yes | — |

### 5.18 `audit_logs`

| Field | Type | Required | Index |
|-------|------|----------|-------|
| `_id` | ObjectId | Yes | PK |
| `user_id` | ObjectId | No | index |
| `action` | string | Yes | index |
| `resource_type` | string | Yes | — |
| `resource_id` | string | No | — |
| `ip_address` | string | No | — |
| `metadata` | dict | No | — |
| `created_at` | datetime | Yes | index |

---

## 6. Repositories

MongoDB access **only**. 18 repositories — one per collection. No AI, Playwright, or HTTP.

| File | Class | Collection |
|------|-------|------------|
| `user_repository.py` | `UserRepository` | `users` |
| `session_repository.py` | `SessionRepository` | `sessions` |
| `profile_repository.py` | `ProfileRepository` | `profiles` |
| `resume_repository.py` | `ResumeRepository` | `resumes` |
| `parsed_resume_repository.py` | `ParsedResumeRepository` | `parsed_resumes` |
| `job_repository.py` | `JobRepository` | `jobs` |
| `company_repository.py` | `CompanyRepository` | `companies` |
| `application_repository.py` | `ApplicationRepository` | `applications` |
| `application_history_repository.py` | `ApplicationHistoryRepository` | `application_history` |
| `recruiter_repository.py` | `RecruiterRepository` | `recruiters` |
| `email_repository.py` | `EmailRepository` | `emails` |
| `notification_repository.py` | `NotificationRepository` | `notifications` |
| `analytics_repository.py` | `AnalyticsRepository` | `analytics` |
| `scheduler_log_repository.py` | `SchedulerLogRepository` | `scheduler_logs` |
| `ai_log_repository.py` | `AILogRepository` | `ai_logs` |
| `prompt_log_repository.py` | `PromptLogRepository` | `prompt_logs` |
| `settings_repository.py` | `SettingsRepository` | `settings` |
| `audit_log_repository.py` | `AuditLogRepository` | `audit_logs` |

---

## 7. Services

Business logic **only**. Services call repositories and **publish events** — never `worker.delay()` directly.

### 7.1 `services/auth/`

| File | Class | Methods |
|------|-------|---------|
| `auth_service.py` | `AuthService` | `register`, `login`, `refresh`, `forgot_password`, `reset_password`, `logout` |

### 7.2 `services/resume/`

| File | Class | Methods |
|------|-------|---------|
| `resume_service.py` | `ResumeService` | `upload` → `events.resume_uploaded`, `list`, `get`, `update_parsed`, `delete`, `reparse`, `download` |

> Parsing is **not** in services. `resume_parser` worker handles parse via `ai/` + repositories.

### 7.3 `services/jobs/`

| File | Class | Methods |
|------|-------|---------|
| `job_service.py` | `JobService` | `search`, `get`, `trigger_collection`, `deduplicate_and_store`, `list_sources` |

> Collection orchestration is triggered by scheduler → `job_scraper` worker, not JobService directly.

### 7.4 `services/application/`

| File | Class | Methods |
|------|-------|---------|
| `application_service.py` | `ApplicationService` | `create`, `list`, `get`, `update_status`, `apply` → `events.application_submitted` |

**Apply Job flow:**
```
apply(job_id) → validate → optimize resume (event) → ApplicationRepository.create()
→ ApplicationHistoryRepository.log() → events.application_submitted.publish()
```

### 7.5 `services/ats/`

| File | Class | Methods |
|------|-------|---------|
| `ats_service.py` | `ATSService` | `fill_form`, `upload_resume`, `capture_screenshot` |

> Called **only** by `ats_apply` worker. Not from API layer directly.

### 7.6 `services/recruiter/`

| File | Class | Methods |
|------|-------|---------|
| `recruiter_service.py` | `RecruiterService` | `discover`, `list`, `get` |

### 7.7 `services/email/`

| File | Class | Methods |
|------|-------|---------|
| `email_service.py` | `EmailService` | `send_via_smtp`, `render_template` |

> Called by `recruiter_email` worker only.

### 7.8 `services/analytics/`

| File | Class | Methods |
|------|-------|---------|
| `analytics_service.py` | `AnalyticsService` | `overview`, `funnel`, `sources`, `scores` |

### 7.9 `services/notifications/`

| File | Class | Methods |
|------|-------|---------|
| `notification_service.py` | `NotificationService` | `create`, `list`, `mark_read`, `mark_all_read` |

### 7.10 `services/profile/`

| File | Class | Methods |
|------|-------|---------|
| `profile_service.py` | `ProfileService` | `get`, `update` |

### 7.11 `services/ai_assistant/`

| File | Class | Methods |
|------|-------|---------|
| `ai_assistant_service.py` | `AIAssistantService` | `chat`, `get_suggestions` |

> Calls `ai/` modules only. Persists via `AILogRepository`, `PromptLogRepository`.

---

## 8. Celery Workers & Tasks

Background processing **only**. One file per worker. Workers may call `ai/`, `collectors/`, `services/`, `repositories/`, and publish `events/`.

| Worker File | Queue | Key Tasks |
|-------------|-------|-----------|
| `resume_parser.py` | `resume` | `parse_resume` |
| `job_scraper.py` | `scraping` | `collect_jobs` → `events.jobs_collected` |
| `job_matcher.py` | `matching` | `score_all`, `score_user` → `events.job_matched` |
| `resume_optimizer.py` | `ai` | `optimize_resume` |
| `cover_letter.py` | `ai` | `generate_cover_letter` |
| `ats_apply.py` | `ats` | `apply_to_job`, `process_queue` |
| `recruiter_email.py` | `email` | `send_email`, `process_queue` → `events.email_sent` |
| `analytics.py` | `analytics` | `aggregate`, `record_email_sent` |
| `notification.py` | `notifications` | `notify_match`, `notify_application` |
| `cleanup.py` | `maintenance` | `run`, `health_check` |

### 8.1 `workers/resume_parser.py`

```
parse_resume(resume_id):
  → ResumeRepository.get()
  → PyMuPDF/pdfplumber extract text
  → ai/resume_extraction.extract()  # no DB in ai/
  → ParsedResumeRepository.create()
  → AILogRepository.log()
  → events (downstream matching)
```

### 8.2 `workers/job_scraper.py`

```
collect_jobs():
  → for collector in enabled: collectors/{source}.collect()
  → JobRepository.bulk_upsert()
  → events.jobs_collected.publish()
```

### 8.3 `workers/job_matcher.py`

```
score_all():
  → for user: ai/resume_matching.score()
  → ApplicationRepository.upsert_match()
  → events.job_matched.publish() if score > threshold
```

### 8.4 `workers/ats_apply.py`

```
process_queue():  # triggered 9 AM daily
apply_to_job(application_id):
  → ATSService.fill_form() via Playwright
  → ApplicationRepository.update(applied)
  → ApplicationHistoryRepository.log()
  → Screenshot saved
```

### 8.5 `workers/recruiter_email.py`

```
process_queue():  # triggered 10 AM daily
send_email(recruiter_id, application_id):
  → ai/recruiter_email.generate()
  → EmailRepository.create()
  → EmailService.send_via_smtp()
  → events.email_sent.publish()
```

---

## 9. Celery Queues

| Queue | Worker File | Priority |
|-------|-------------|----------|
| `resume` | `resume_parser.py` | High |
| `scraping` | `job_scraper.py` | Low |
| `matching` | `job_matcher.py` | Medium |
| `ai` | `resume_optimizer.py`, `cover_letter.py` | Medium |
| `ats` | `ats_apply.py` | High |
| `email` | `recruiter_email.py` | Medium |
| `analytics` | `analytics.py` | Low |
| `notifications` | `notification.py` | High |
| `maintenance` | `cleanup.py` | Lowest |

---

## 10. Scheduler / Cron Jobs

`scheduler/` contains **only** cron registration. No scraping, AI, or business logic.

| Job ID | Cron | Triggers | Description |
|--------|------|----------|-------------|
| `collect_jobs` | `0 * * * *` | `job_scraper.collect_jobs` | Every hour |
| `score_jobs` | `*/30 * * * *` | `job_matcher.score_all` | Every 30 min |
| `ats_apply` | `0 9 * * *` | `ats_apply.process_queue` | Daily 9 AM UTC |
| `recruiter_email` | `0 10 * * *` | `recruiter_email.process_queue` | Daily 10 AM UTC |
| `aggregate_analytics` | `0 * * * *` | `analytics.aggregate` | Every hour |
| `cleanup` | `0 3 * * 0` | `cleanup.run` | Sunday 3 AM UTC |
| `health_check` | `*/5 * * * *` | `cleanup.health_check` | Every 5 min |

---

## 11. AI Prompts

Prompts stored in `prompts/` (files) and documented in `docs/AI_PROMPTS.md`.

| Prompt File | Used By | Purpose |
|-------------|---------|---------|
| `prompts/resume_matching.md` | `ai/resume_matching/` | Score resume vs JD |
| `prompts/cover_letter.md` | `ai/cover_letter/` | Generate cover letter |
| `prompts/recruiter_email.md` | `ai/recruiter_email/` | Generate outreach email |
| `prompts/ats_optimizer.md` | `ai/resume_matching/` | Optimize resume for ATS |
| `prompts/interview_questions.md` | `ai/interview/` | Interview prep (v2) |
| `prompts/resume_extraction.md` | `ai/resume_extraction/` | Extract structured fields |

---

## 12. Job Collectors

Each collector in `backend/app/collectors/{source}/` implements `BaseCollector`:

```python
class BaseCollector(ABC):
    @abstractmethod
    async def collect(self) -> list[RawJob]: ...
    
    @abstractmethod
    def get_source_name(self) -> str: ...
```

| Collector Module | Source Name | Config Key |
|-----------------|-------------|------------|
| `collectors/greenhouse/collector.py` | `greenhouse` | `job_sources.yaml → greenhouse` |
| `collectors/lever/collector.py` | `lever` | `job_sources.yaml → lever` |
| `collectors/ashby/collector.py` | `ashby` | `job_sources.yaml → ashby` |
| `collectors/company_sites/collector.py` | `company_sites` | `companies.yaml` |
| `collectors/linkedin/collector.py` | `linkedin` | `job_sources.yaml → linkedin` |
| `collectors/naukri/collector.py` | `naukri` | `job_sources.yaml → naukri` |
| `collectors/indeed/collector.py` | `indeed` | `job_sources.yaml → indeed` |
| `collectors/wellfound/collector.py` | `wellfound` | `job_sources.yaml → wellfound` |

---

## 13. Domain Events (`backend/app/events/`)

Events decouple services from workers. **Services publish. Workers consume.**

| File | Event | Publisher | Worker Triggered |
|------|-------|-----------|------------------|
| `resume_uploaded.py` | `resume_uploaded` | `ResumeService.upload()` | `resume_parser.parse_resume` |
| `jobs_collected.py` | `jobs_collected` | `job_scraper` worker | `job_matcher.score_all` |
| `job_matched.py` | `job_matched` | `job_matcher` worker | `notification.notify_match` |
| `application_submitted.py` | `application_submitted` | `ApplicationService.apply()` | `ats_apply.apply_to_job` |
| `email_sent.py` | `email_sent` | `recruiter_email` worker | `analytics.record_email_sent`, `notification.notify` |

### Event Pattern

```python
# events/application_submitted.py
def publish(application_id: str, user_id: str) -> None:
    from app.workers.ats_apply import apply_to_job
    apply_to_job.delay(application_id)
```

### Extended Event Catalog

| Event | Payload | Published By | Consumed By |
|-------|---------|--------------|-------------|
| `resume_uploaded` | `{resume_id, user_id}` | ResumeService | `resume_parser` |
| `jobs_collected` | `{count, sources}` | `job_scraper` | `job_matcher` |
| `job_matched` | `{user_id, application_id, score}` | `job_matcher` | `notification` |
| `application_submitted` | `{application_id, user_id}` | ApplicationService | `ats_apply` |
| `application_applied` | `{application_id}` | `ats_apply` | `analytics`, `notification` |
| `email_sent` | `{email_id, user_id, application_id}` | `recruiter_email` | `analytics`, `notification` |

---

## 14. Docker Containers

| Container | Image / Build | Ports | Volumes | Depends On |
|-----------|--------------|-------|---------|------------|
| `nginx` | `nginx:alpine` + `docker/nginx/` | 80, 443 | — | frontend, api |
| `frontend` | `frontend/Dockerfile` | 5173 (dev) | — | — |
| `api` | `backend/Dockerfile` | 8000 | uploads | mongodb, redis, ollama |
| `celery-worker` | `backend/Dockerfile` | — | uploads, playwright-data | mongodb, redis, ollama |
| `celery-beat` | `backend/Dockerfile` | — | — | redis |
| `mongodb` | `mongo:7` | 27017 | mongo-data | — |
| `redis` | `redis:7-alpine` | 6379 | redis-data | — |
| `ollama` | `ollama/ollama` | 11434 | ollama-data | — |
| `prometheus` (optional) | `prom/prometheus` | 9090 | — | api |
| `grafana` (optional) | `grafana/grafana` | 3000 | — | prometheus |

---

## 15. Frontend Pages

| Page | File | Route | Purpose |
|------|------|-------|---------|
| Login | `LoginPage.tsx` | `/login` | User login |
| Register | `RegisterPage.tsx` | `/register` | User registration |
| Forgot Password | `ForgotPasswordPage.tsx` | `/forgot-password` | Password reset |
| Dashboard | `DashboardPage.tsx` | `/dashboard` | Overview + funnel |
| Resume Manager | `ResumeManagerPage.tsx` | `/resumes` | Upload, list, manage resumes |
| Job Explorer | `JobExplorerPage.tsx` | `/jobs` | Search, browse, view matches |
| Applications | `ApplicationsPage.tsx` | `/applications` | Track application pipeline |
| Analytics | `AnalyticsPage.tsx` | `/analytics` | Charts, funnel, sources |
| AI Assistant | `AIAssistantPage.tsx` | `/assistant` | Chat with AI about jobs/resume |
| Settings | `SettingsPage.tsx` | `/settings` | Automation, sources, preferences |
| Notifications | `NotificationsPage.tsx` | `/notifications` | Notification center |
| Profile | `ProfilePage.tsx` | `/profile` | Edit profile, links, bio |

### Detail Sub-Routes (nested)

| Page | Route |
|------|-------|
| Resume Detail | `/resumes/:id` |
| Job Detail | `/jobs/:id` |
| Application Detail | `/applications/:id` |

---

## 16. Frontend Components

| Component | Location | Used By |
|-----------|----------|---------|
| `Navbar` | `components/layout/Navbar.tsx` | All authenticated pages |
| `Sidebar` | `components/layout/Sidebar.tsx` | Dashboard layout |
| `Footer` | `components/layout/Footer.tsx` | All pages |
| `AuthLayout` | `layouts/AuthLayout.tsx` | Login, Register |
| `DashboardLayout` | `layouts/DashboardLayout.tsx` | All app pages |
| `ResumeUploader` | `components/resume/ResumeUploader.tsx` | ResumesPage |
| `ResumeCard` | `components/resume/ResumeCard.tsx` | ResumesPage |
| `ParsedResumeView` | `components/resume/ParsedResumeView.tsx` | ResumeDetailPage |
| `ResumeEditor` | `components/resume/ResumeEditor.tsx` | ResumeDetailPage |
| `JobCard` | `components/jobs/JobCard.tsx` | JobsPage, MatchesPage |
| `JobFilters` | `components/jobs/JobFilters.tsx` | JobsPage |
| `MatchScoreBadge` | `components/jobs/MatchScoreBadge.tsx` | MatchesPage, JobCard |
| `MatchExplanation` | `components/jobs/MatchExplanation.tsx` | MatchesPage |
| `ApplicationCard` | `components/applications/ApplicationCard.tsx` | ApplicationsPage |
| `ApplicationTimeline` | `components/applications/ApplicationTimeline.tsx` | ApplicationDetailPage |
| `CoverLetterView` | `components/applications/CoverLetterView.tsx` | ApplicationDetailPage |
| `StatusBadge` | `components/common/StatusBadge.tsx` | ApplicationCard |
| `AnalyticsChart` | `components/analytics/AnalyticsChart.tsx` | AnalyticsPage |
| `FunnelChart` | `components/analytics/FunnelChart.tsx` | AnalyticsPage |
| `SourceBreakdown` | `components/analytics/SourceBreakdown.tsx` | AnalyticsPage |
| `NotificationBell` | `components/notifications/NotificationBell.tsx` | Navbar |
| `NotificationItem` | `components/notifications/NotificationItem.tsx` | NotificationsPage |
| `SettingsForm` | `components/settings/SettingsForm.tsx` | SettingsPage |
| `AutomationToggle` | `components/settings/AutomationToggle.tsx` | SettingsPage |
| `LoadingSpinner` | `components/common/LoadingSpinner.tsx` | Global |
| `ErrorBoundary` | `components/common/ErrorBoundary.tsx` | App root |
| `ConfirmDialog` | `components/common/ConfirmDialog.tsx` | Apply actions |
| `EmptyState` | `components/common/EmptyState.tsx` | List pages |
| `Pagination` | `components/common/Pagination.tsx` | List pages |

---

## 17. Frontend Routes

| Path | Component | Layout | Auth |
|------|-----------|--------|------|
| `/login` | `LoginPage` | `AuthLayout` | No |
| `/register` | `RegisterPage` | `AuthLayout` | No |
| `/forgot-password` | `ForgotPasswordPage` | `AuthLayout` | No |
| `/dashboard` | `DashboardPage` | `DashboardLayout` | Yes |
| `/resumes` | `ResumeManagerPage` | `DashboardLayout` | Yes |
| `/resumes/:id` | `ResumeDetailPage` | `DashboardLayout` | Yes |
| `/jobs` | `JobExplorerPage` | `DashboardLayout` | Yes |
| `/jobs/:id` | `JobDetailPage` | `DashboardLayout` | Yes |
| `/applications` | `ApplicationsPage` | `DashboardLayout` | Yes |
| `/applications/:id` | `ApplicationDetailPage` | `DashboardLayout` | Yes |
| `/analytics` | `AnalyticsPage` | `DashboardLayout` | Yes |
| `/assistant` | `AIAssistantPage` | `DashboardLayout` | Yes |
| `/settings` | `SettingsPage` | `DashboardLayout` | Yes |
| `/notifications` | `NotificationsPage` | `DashboardLayout` | Yes |
| `/profile` | `ProfilePage` | `DashboardLayout` | Yes |
| `/` | redirect → `/dashboard` | — | — |
| `*` | `NotFoundPage` | — | — |

---

## 18. Frontend Services & State

### 18.1 API Services (`frontend/src/services/`)

| File | Functions |
|------|-----------|
| `api.ts` | Axios instance, interceptors, token refresh |
| `authService.ts` | `login`, `register`, `refresh`, `logout` |
| `resumeService.ts` | `upload`, `list`, `get`, `update`, `delete`, `reparse` |
| `jobService.ts` | `search`, `get`, `collect`, `listSources` |
| `applicationService.ts` | `list`, `get`, `create`, `updateStatus`, `apply`, `optimize` |
| `recruiterService.ts` | `list`, `discover`, `sendEmail` |
| `analyticsService.ts` | `overview`, `funnel`, `sources`, `scores` |
| `dashboardService.ts` | `getDashboard` |
| `notificationService.ts` | `list`, `markRead`, `markAllRead` |
| `settingsService.ts` | `get`, `update` |

### 18.2 State Stores (`frontend/src/store/`)

| Store | State | Actions |
|-------|-------|---------|
| `authStore.ts` | user, tokens, isAuthenticated | login, logout, refresh |
| `notificationStore.ts` | notifications, unreadCount | fetch, markRead |
| `settingsStore.ts` | settings | fetch, update |

### 18.3 Types (`frontend/src/types/`)

| File | Interfaces |
|------|-----------|
| `auth.ts` | User, TokenResponse, LoginRequest |
| `resume.ts` | Resume, ParsedResume, Experience, Education |
| `job.ts` | Job, JobDetail, JobSearchParams |
| `application.ts` | Application, ApplicationDetail, ApplicationStatus |
| `analytics.ts` | AnalyticsOverview, Funnel, SourceBreakdown |
| `notification.ts` | Notification |
| `settings.ts` | Settings, AutomationMode |

---

## 19. Configuration Files

| File | Purpose |
|------|---------|
| `configs/settings.yaml` | App-level settings (non-secret) |
| `configs/scheduler.yaml` | Cron job definitions |
| `configs/job_sources.yaml` | Collector enable/disable + URLs |
| `configs/ai.yaml` | Ollama models, matching weights |
| `configs/companies.yaml` | Company career page selectors |

---

## 20. Environment Variables

All defined in `.env.example`. Copy to `.env` and fill in values before running the app.

**Rule**: Every new env var must be added to `.env.example`, `app/config.py`, and this section.

### Required

| Variable | Settings field | Description |
|----------|----------------|-------------|
| `APP_SECRET_KEY` | `app_secret_key` | Application secret (16+ chars; 32+ in production) |
| `API_BASE_URL` | `api_base_url` | Public API origin, e.g. `http://localhost:8000` |
| `CORS_ORIGINS` | `cors_origins` | Comma-separated allowed origins |
| `MONGODB_URI` | `mongodb_uri` | MongoDB connection string |
| `MONGODB_DB_NAME` | `mongodb_db_name` | Database name |
| `REDIS_URL` | `redis_url` | Redis connection URL |
| `CELERY_BROKER_URL` | `celery_broker_url` | Celery broker |
| `CELERY_RESULT_BACKEND` | `celery_result_backend` | Celery result backend |
| `JWT_SECRET_KEY` | `jwt_secret_key` | JWT signing secret |
| `OLLAMA_BASE_URL` | `ollama_base_url` | Ollama API base URL |
| `OLLAMA_MODEL` | `ollama_model` | Default LLM model |
| `OLLAMA_EMBEDDING_MODEL` | `ollama_embedding_model` | Embedding model |
| `FRONTEND_BASE_URL` | `frontend_base_url` | SPA origin for email links |
| `STORAGE_ROOT` | `storage_root` | On-disk storage root |
| `RESUME_STORAGE_DIR` | `resume_storage_dir` | Subdir for uploaded resumes |

### Optional (defaults in Settings)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `AI Job Agent` | Display name |
| `APP_ENV` | `development` | `development` \| `production` \| `testing` |
| `APP_DEBUG` | `true` | Debug mode |
| `API_V1_PREFIX` | `/api/v1` | API route prefix |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `PROMPTS_DIR` | `prompts` | LLM prompt files |
| `CONFIGS_DIR` | `configs` | YAML config directory |
| `EMAIL_VERIFICATION_EXPIRE_HOURS` | `24` | Verification link TTL |
| `SMTP_HOST` | `""` | SMTP server (empty = log links to console) |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | `""` | SMTP username |
| `SMTP_PASSWORD` | `""` | SMTP password |
| `SMTP_FROM_EMAIL` | `""` | From address |
| `STORAGE_PROVIDER` | `local` | Storage backend |
| `GENERATED_RESUME_DIR` | `generated-resumes` | Optimized resume subdir |
| `COVER_LETTER_DIR` | `cover-letters` | Cover letter subdir |
| `PROFILE_IMAGE_DIR` | `profile-images` | Profile image subdir |
| `TEMP_DIR` | `temp` | Temp file subdir |
| `MAX_RESUME_SIZE_MB` | `10` | Max upload size |
| `ALLOWED_RESUME_EXTENSIONS` | `pdf` | Comma-separated extensions |
| `VITE_API_BASE_URL` | — | Frontend build-time API URL |

See [DEPLOYMENT.md](DEPLOYMENT.md) for per-environment values.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial LLD from Engineering Blueprint |
| 0.2.0 | 2026-07-10 | SRP layers, events/, 18 collections, 10 workers, 12 pages, scheduler update |
| 0.3.0 | 2026-07-11 | Settings refactor: env-only secrets, storage path configuration |
