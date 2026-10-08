# Database Design — AI Job Agent

**Version**: 0.4.2  
**Engine**: MongoDB 7.x  
**ODM**: Beanie (async)  
**MVP Collections**: 12  
**Full Platform Collections**: 19 (7 deferred post-MVP)  
**Last Updated**: 2026-10-08

---

## MVP Scope Decision

Build the **smallest database surface** that supports the MVP pipeline end-to-end. Do not create collections, indexes, or repositories for features that are not in MVP.

### MVP Features → Collections

| MVP Feature | Collections Used |
|-------------|------------------|
| Email registration + login + JWT | `users`, `sessions` |
| User profile on dashboard | `profiles` |
| Resume upload | `resumes` |
| Resume parsing + embeddings | `parsed_resumes` |
| Greenhouse job collector | `jobs`, `companies`, `scheduler_logs` |
| Resume-specific job matching | `job_matches`, `jobs`, `resumes`, `parsed_resumes` |
| Ollama job matching (phase 2) | `applications`, `ai_logs`, `settings` |
| Dashboard (counts, matches, jobs) | `applications`, `jobs`, `resumes`, `parsed_resumes` |

### In MVP (12 collections)

| # | Collection | Repository | Purpose |
|---|------------|------------|---------|
| 1 | `users` | `UserRepository` | Auth credentials |
| 2 | `sessions` | `SessionRepository` | Refresh tokens / active sessions |
| 3 | `profiles` | `ProfileRepository` | Display name, headline, location |
| 4 | `resumes` | `ResumeRepository` | Uploaded file metadata |
| 5 | `parsed_resumes` | `ParsedResumeRepository` | Structured resume + Ollama embedding |
| 6 | `companies` | `CompanyRepository` | Greenhouse board registry |
| 7 | `jobs` | `JobRepository` | Collected job listings |
| 8 | `job_matches` | `JobMatchRepository` | Resume-scoped match cache (`resume_id` + `job_id`) |
| 9 | `applications` | `ApplicationRepository` | Later apply pipeline (one row per user + job) |
| 10 | `settings` | `SettingsRepository` | Match threshold, job preferences |
| 11 | `scheduler_logs` | `SchedulerLogRepository` | Collector cron execution logs |
| 12 | `ai_logs` | `AILogRepository` | Ollama request metrics |

### Deferred Post-MVP (7 collections)

These remain in the **full platform contract** ([LLD.md](LLD.md) §5) but are **not created during MVP implementation**.

| Collection | Deferred Until | Reason |
|------------|----------------|--------|
| `application_history` | Phase 5 (ATS apply) | Status audit trail not needed for match-only MVP |
| `recruiters` | Phase 6 (outreach) | No recruiter discovery in MVP |
| `emails` | Phase 6 (outreach) | No email sending in MVP |
| `notifications` | Phase 6 | Dashboard polling suffices for MVP |
| `analytics` | Phase 6 | Dashboard queries live collections directly |
| `prompt_logs` | Phase 5+ | `ai_logs` covers MVP observability |
| `audit_logs` | Phase 7 (hardening) | Security audit not required for MVP |

---

## Architecture Rules

- One collection → one Beanie model → one repository. No exceptions.
- Repositories are the **only** layer that touches MongoDB.
- All `ObjectId` foreign keys are stored as `PydanticObjectId`; relationships are **logical** (no MongoDB joins).
- Timestamps use UTC `datetime` unless noted (`date` for analytics only).
- MVP backend initializes Beanie for the implemented collections, including `job_matches`.

---

## Enums (MVP)

```python
class ResumeStatus(str, Enum):
    PENDING = "pending"       # uploaded, parse not started
    PARSING = "parsing"       # worker in progress
    PARSED = "parsed"         # success
    FAILED = "failed"         # parse error

class ApplicationStatus(str, Enum):
    # --- MVP statuses ---
    MATCHED = "matched"       # AI match created, shown on dashboard
    SAVED = "saved"           # user bookmarked
    DISMISSED = "dismissed"   # user hid from dashboard
    # --- Post-MVP (schema reserved, unused in MVP) ---
    SELECTED = "selected"
    OPTIMIZING = "optimizing"
    READY = "ready"
    APPLYING = "applying"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"

class JobSource(str, Enum):
    GREENHOUSE = "greenhouse"  # MVP only source

class SchedulerRunStatus(str, Enum):
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
```

---

## Embedded Documents

### Experience

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `company` | string | Yes | Employer name |
| `title` | string | Yes | Role title |
| `start_date` | string | No | ISO `YYYY-MM` or free text |
| `end_date` | string | No | `null` / `"present"` allowed |
| `description` | string | No | Bullet summary |
| `location` | string | No | City, remote, etc. |

### Project (embedded)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | Yes | Project name |
| `description` | string | No | Summary |
| `technologies` | list[string] | No | Stack used |
| `url` | string | No | Link if present |
| `start_date` | string | No | ISO `YYYY-MM` |
| `end_date` | string | No | End date |

---

### Education

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `institution` | string | Yes | School name |
| `degree` | string | No | e.g. B.S., M.S. |
| `field` | string | No | Major / concentration |
| `start_date` | string | No | ISO `YYYY-MM` |
| `end_date` | string | No | Graduation |

---

## Collection Schemas (MVP)

### 1. `users`

Auth credentials only. Profile data lives in `profiles`.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `email` | string | Yes | — | unique | Lowercase normalized at service layer |
| `password_hash` | string | Yes | — | — | bcrypt |
| `is_active` | bool | Yes | `true` | — | Soft-disable account |
| `email_verified` | bool | Yes | `false` | — | Must be true before login |
| `verification_token_hash` | string | No | — | — | SHA-256 of email verification token |
| `verification_token_expires_at` | datetime | No | — | — | Default 24h from registration |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_users_email` | `{ email: 1 }` | unique |

**Relationships**

- `users` 1 → 1 `profiles`
- `users` 1 → N `sessions`
- `users` 1 → N `resumes`
- `users` 1 → 1 `settings`

---

### 2. `sessions`

Refresh token rotation for JWT auth.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | index | → `users._id` |
| `refresh_token_hash` | string | Yes | — | — | SHA-256 of refresh token |
| `user_agent` | string | No | — | — | Client hint |
| `ip_address` | string | No | — | — | Login IP |
| `expires_at` | datetime | Yes | — | TTL | Refresh expiry (7 days) |
| `revoked` | bool | Yes | `false` | — | Logout / rotation invalidates |
| `created_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_sessions_user_id` | `{ user_id: 1 }` | |
| `idx_sessions_expires_at` | `{ expires_at: 1 }` | `expireAfterSeconds: 0` (TTL on `expires_at`) |

**Relationships**

- `sessions` N → 1 `users`

---

### 3. `profiles`

User-facing identity separate from auth.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | unique | → `users._id` |
| `full_name` | string | Yes | — | — | From registration or resume |
| `headline` | string | No | — | — | e.g. "Senior Backend Engineer" |
| `location` | string | No | — | — | City, country |
| `linkedin_url` | string | No | — | — | |
| `avatar_url` | string | No | — | — | Post-MVP upload |
| `bio` | string | No | — | — | Short summary |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_profiles_user_id` | `{ user_id: 1 }` | unique |

**Relationships**

- `profiles` 1 → 1 `users`

---

### 4. `resumes`

Uploaded file metadata. Binary stored on disk/S3 path in `file_path`.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | index | → `users._id` |
| `filename` | string | Yes | — | — | Original upload name |
| `file_path` | string | Yes | — | — | Relative path under `STORAGE_ROOT/RESUME_STORAGE_DIR` |
| `file_url` | string | No | — | — | Public HTTPS URL at upload time (`{API_BASE_URL}/storage/resumes/{file_path}`); pasteable in browser |
| `file_size` | int | Yes | — | — | Bytes |
| `mime_type` | string | Yes | — | — | `application/pdf`, `application/vnd...docx` |
| `status` | ResumeStatus | Yes | `pending` | index | Worker updates |
| `is_primary` | bool | Yes | `false` | — | One primary per user (enforced in service) |
| `parse_progress` | int | Yes | `0` | — | 0–100, updated at each real parse stage |
| `parse_stage` | string | Yes | `queued` | — | `queued`, `reading`, `extracting`, `analyzing`, `saving`, `complete`, `failed` |
| `parse_error` | string | No | — | — | Short message safe to show in the app. Internal causes are logged only |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_resumes_user_id` | `{ user_id: 1 }` | |
| `idx_resumes_user_status` | `{ user_id: 1, status: 1 }` | Dashboard filter |
| `idx_resumes_user_primary` | `{ user_id: 1, is_primary: 1 }` | Find primary resume |

**Relationships**

- `resumes` N → 1 `users`
- `resumes` 1 → 0..1 `parsed_resumes`

---

### 5. `parsed_resumes`

Structured output from resume parser + Ollama embedding for matching.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `resume_id` | ObjectId | Yes | — | unique | → `resumes._id` |
| `user_id` | ObjectId | Yes | — | index | Denormalized for user queries |
| `name` | string | No | — | — | Extracted full name |
| `email` | string | No | — | — | Extracted email |
| `phone` | string | No | — | — | |
| `skills` | list[string] | No | `[]` | — | From Ollama extraction |
| `experience` | list[Experience] | No | `[]` | — | From Ollama extraction |
| `projects` | list[Project] | No | `[]` | — | From Ollama extraction |
| `education` | list[Education] | No | `[]` | — | Embedded |
| `summary` | string | No | — | — | Professional summary |
| `raw_text` | string | No | — | text | Full extracted text |
| `embedding` | list[float] | No | — | — | `nomic-embed-text`, dim 768 |
| `embedding_model` | string | No | — | — | e.g. `nomic-embed-text` |
| `parser_version` | string | Yes | — | — | e.g. `pymupdf-1.24` |
| `parsed_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | Manual edit timestamp |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_parsed_resumes_resume_id` | `{ resume_id: 1 }` | unique |
| `idx_parsed_resumes_user_id` | `{ user_id: 1 }` | |
| `idx_parsed_resumes_text` | `{ raw_text: "text", summary: "text", skills: "text" }` | Full-text search (optional MVP) |

**Relationships**

- `parsed_resumes` 1 → 1 `resumes`
- `parsed_resumes` N → 1 `users`

---

### 6. `companies`

Greenhouse board registry. Collector reads enabled boards from here (seeded via config).

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `name` | string | Yes | — | unique | Display name |
| `slug` | string | Yes | — | unique | Greenhouse board token |
| `website` | string | No | — | — | |
| `ats_type` | string | Yes | `greenhouse` | index | MVP: always greenhouse |
| `careers_url` | string | No | — | — | Full board URL |
| `enabled` | bool | Yes | `true` | index | Skip disabled boards |
| `last_collected_at` | datetime | No | — | — | Per-board watermark |
| `created_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_companies_name` | `{ name: 1 }` | unique |
| `idx_companies_slug` | `{ slug: 1 }` | unique |
| `idx_companies_enabled_ats` | `{ enabled: 1, ats_type: 1 }` | Collector query |

**Relationships**

- `companies` 1 → N `jobs`

---

### 7. `jobs`

Discovered listings from Greenhouse collector.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `title` | string | Yes | — | text | |
| `company` | string | Yes | — | index | Denormalized company name |
| `company_id` | ObjectId | No | — | index | → `companies._id` |
| `location` | string | No | — | — | |
| `description` | string | Yes | — | text | Full JD text |
| `requirements` | string | No | — | — | Extracted requirements block |
| `source` | JobSource | Yes | `greenhouse` | index | MVP: greenhouse only |
| `source_id` | string | Yes | — | compound | Greenhouse job ID |
| `source_url` | string | No | — | — | Public posting URL |
| `apply_url` | string | Yes | — | — | Application link |
| `department` | string | No | — | — | From Greenhouse metadata |
| `employment_type` | string | No | — | — | full_time, contract, etc. |
| `salary_min` | int | No | — | — | USD cents optional |
| `salary_max` | int | No | — | — | |
| `remote` | bool | No | — | index | Derived from location/JD |
| `posted_at` | datetime | No | — | index | Source posting date |
| `collected_at` | datetime | Yes | now | TTL | Last scrape time |
| `is_active` | bool | Yes | `true` | index | False when delisted |
| `embedding` | list[float] | No | — | — | Job JD embedding for similarity |
| `embedding_model` | string | No | — | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_jobs_source_dedup` | `{ source: 1, source_id: 1 }` | unique — dedup key |
| `idx_jobs_company_id` | `{ company_id: 1 }` | |
| `idx_jobs_posted_at` | `{ posted_at: -1 }` | Recent jobs first |
| `idx_jobs_remote_active` | `{ remote: 1, is_active: 1 }` | Filter |
| `idx_jobs_text` | `{ title: "text", description: "text" }` | Search |
| `idx_jobs_collected_ttl` | `{ collected_at: 1 }` | `expireAfterSeconds: 7776000` (90 days) — inactive jobs only via `is_active: false` cleanup worker post-MVP; TTL is safety net |

**Relationships**

- `jobs` N → 1 `companies` (optional FK)
- `jobs` 1 → N `applications`

---

### 8. `applications`

Match records produced by Ollama job matcher. **This is the core MVP output entity.**

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | index | → `users._id` |
| `job_id` | ObjectId | Yes | — | index | → `jobs._id` |
| `resume_id` | ObjectId | Yes | — | — | Primary resume used for match |
| `parsed_resume_id` | ObjectId | Yes | — | — | Snapshot reference |
| `status` | ApplicationStatus | Yes | `matched` | index | MVP: matched/saved/dismissed |
| `match_score` | float | Yes | — | index | 0–100 from Ollama |
| `match_explanation` | string | Yes | — | — | Human-readable rationale |
| `match_factors` | dict | No | — | — | `{ skills: 85, experience: 70, ... }` |
| `embedding_similarity` | float | No | — | — | Cosine sim pre-filter score |
| `matched_at` | datetime | Yes | now | index | |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_applications_user_job` | `{ user_id: 1, job_id: 1 }` | unique — one application row per user+job. Resume-specific scores live in `job_matches` |
| `idx_applications_user_status_score` | `{ user_id: 1, status: 1, match_score: -1 }` | Dashboard sorted list |
| `idx_applications_user_matched_at` | `{ user_id: 1, matched_at: -1 }` | Recent matches |

**Relationships**

- `applications` N → 1 `users`
- `applications` N → 1 `jobs`
- `applications` N → 1 `resumes`

---

### 9. `settings`

Per-user automation and matching preferences. Created on registration with defaults.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | unique | → `users._id` |
| `match_threshold` | float | Yes | `70.0` | — | Min score to surface match |
| `preferred_locations` | list[string] | No | `[]` | — | e.g. `["Remote", "San Francisco"]` |
| `preferred_titles` | list[string] | No | `[]` | — | Title keywords |
| `preferred_skills` | list[string] | No | `[]` | — | Must-have skills boost |
| `remote_only` | bool | Yes | `false` | — | Filter jobs |
| `enabled_sources` | list[string] | No | `["greenhouse"]` | — | MVP: greenhouse only |
| `ai_model` | string | Yes | `llama3.2` | — | Ollama generation model |
| `embedding_model` | string | Yes | `nomic-embed-text` | — | |
| `auto_match_enabled` | bool | Yes | `true` | — | Run matcher after job collect |
| `email_notifications` | bool | Yes | `true` | — | Post-MVP delivery |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_settings_user_id` | `{ user_id: 1 }` | unique |

**Relationships**

- `settings` 1 → 1 `users`

---

### 10. `scheduler_logs`

Cron execution audit for Greenhouse collector (and future schedulers).

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `job_name` | string | Yes | — | index | e.g. `collect_greenhouse` |
| `status` | SchedulerRunStatus | Yes | — | index | |
| `started_at` | datetime | Yes | now | index | |
| `completed_at` | datetime | No | — | — | |
| `duration_ms` | int | No | — | — | |
| `records_processed` | int | No | `0` | — | Jobs inserted/updated |
| `records_failed` | int | No | `0` | — | |
| `error` | string | No | — | — | Stack trace summary |
| `metadata` | dict | No | — | — | `{ company_slug, board_count, ... }` |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_scheduler_logs_job_started` | `{ job_name: 1, started_at: -1 }` | Recent runs |
| `idx_scheduler_logs_status` | `{ status: 1, started_at: -1 }` | Failures |

**Relationships**

- Standalone operational log (no FK)

---

### 11. `ai_logs`

Ollama call observability for resume embedding and job matching.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | No | — | index | Null for system/batch jobs |
| `operation` | string | Yes | — | index | `embed_resume`, `match_job`, `score_match` |
| `model` | string | Yes | — | — | Ollama model name |
| `reference_type` | string | No | — | — | `resume`, `job`, `application` |
| `reference_id` | ObjectId | No | — | — | Related document |
| `input_tokens` | int | No | — | — | Estimated |
| `output_tokens` | int | No | — | — | Estimated |
| `duration_ms` | int | Yes | — | — | |
| `success` | bool | Yes | — | index | |
| `error` | string | No | — | — | |
| `created_at` | datetime | Yes | now | index | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `idx_ai_logs_user_operation` | `{ user_id: 1, operation: 1, created_at: -1 }` | |
| `idx_ai_logs_created_at` | `{ created_at: -1 }` | Recent logs |

**Relationships**

- Optional logical FK to `users`, `resumes`, `jobs`, `applications` via `reference_*`

---

### 12. `job_matches`

Cache of deterministic match scores. The cache key is `resume_id` + `job_id`, so the same Greenhouse job can have different scores for two resumes of one user.

| Field | Type | Required | Default | Index | Notes |
|-------|------|----------|---------|-------|-------|
| `_id` | ObjectId | Yes | auto | PK | |
| `user_id` | ObjectId | Yes | — | index | Owner; must match the authenticated user |
| `resume_id` | ObjectId | Yes | — | index | → `resumes._id` |
| `job_id` | ObjectId | Yes | — | index | → `jobs._id` |
| `match_score` | int | Yes | — | — | 0–100 |
| `matched_skills` | list[string] | Yes | `[]` | — | |
| `missing_skills` | list[string] | Yes | `[]` | — | |
| `matched_role` | bool | Yes | `false` | — | |
| `experience_match` | bool | Yes | `false` | — | |
| `project_matches` | list[string] | Yes | `[]` | — | |
| `match_reasons` | list[string] | Yes | `[]` | — | |
| `title` | string | Yes | — | — | Denormalized for list pages |
| `company` | string | Yes | — | — | Denormalized |
| `location` | string | No | — | — | |
| `url` | string | Yes | — | — | Apply URL |
| `remote` | bool | No | — | — | |
| `posted_at` | datetime | No | — | — | |
| `profile_updated_at` | datetime | Yes | — | — | Invalidates when the parsed resume changes |
| `active_job_count` | int | Yes | — | — | Active jobs at scoring time |
| `latest_job_collected_at` | datetime | No | — | — | Invalidates when collection changes |
| `min_score` | int | Yes | — | — | Threshold used when the row was written |
| `scorer_version` | string | Yes | — | — | `deterministic-v1` |
| `created_at` | datetime | Yes | now | — | |
| `updated_at` | datetime | Yes | now | — | |

**Indexes**

| Name | Keys | Options |
|------|------|---------|
| `resume_id_1_job_id_1` | `{ resume_id: 1, job_id: 1 }` | unique |
| `user_id_1_resume_id_1_match_score_-1` | `{ user_id: 1, resume_id: 1, match_score: -1 }` | Sorted match list |

**Relationships**

- `job_matches` N → 1 `resumes`
- `job_matches` N → 1 `jobs`
- `job_matches` N → 1 `users`

Only rows at or above the match threshold are stored. A cache miss recomputes scores for that resume.

---

## Entity Relationship Diagram (MVP)

```
                              ┌─────────────┐
                              │   users     │
                              └──────┬──────┘
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  sessions   │          │  profiles   │          │  settings   │
    │   (N:1)     │          │   (1:1)     │          │   (1:1)     │
    └─────────────┘          └─────────────┘          └─────────────┘
           │
           │ user_id
           ▼
    ┌─────────────┐          ┌─────────────────┐
    │   resumes   │───1:1───▶│ parsed_resumes  │
    │   (N:1)     │          │                 │
    └──────┬──────┘          └────────┬────────┘
           │                          │
           │                          │ embedding used by matcher
           │                          ▼
    ┌─────────────┐          ┌─────────────────┐         ┌───────────────┐
    │ companies   │───1:N───▶│      jobs       │───N:1──▶│ applications  │
    │             │          │                 │         │  (user+job)   │
    └─────────────┘          └─────────────────┘         └───────────────┘
           ▲                                                    ▲
           │                                                    │
    ┌──────┴──────┐                                    ┌──────┴──────┐
    │scheduler_logs│                                   │   ai_logs   │
    │  (standalone)│                                   │ (optional FK)│
    └─────────────┘                                    └─────────────┘
```

---

## MVP Data Flow

```
Register → users + profiles + settings (default)
Login    → sessions (refresh token)
Upload   → resumes (status: pending)
Parse    → parsed_resumes + resumes.status = parsed + ai_logs (embed)
Collect  → scheduler_logs + jobs (+ companies watermark)
Match    → applications + ai_logs (score)
Dashboard→ query applications (status ≠ dismissed), jobs, resumes
```

---

## Phase 2 — Backend Foundation (No Business Logic)

Phase 2 implements **infrastructure only**. These layers touch MongoDB but do not run parsers, collectors, or matchers.

| Layer | MVP DB Touchpoint |
|-------|-------------------|
| `config.py` | `MONGODB_URI`, `MONGODB_DB_NAME` |
| `db/client.py` | Motor client + Beanie init for 11 MVP models |
| `db/init_db.py` | Create indexes from this document |
| `core/jwt.py` | No collection writes (stateless access token) |
| `api/v1/health/` | Ping MongoDB (`db.command("ping")`) |
| Swagger | Auto-generated from FastAPI (no extra collections) |

**Not in Phase 2**: repositories with business queries, Celery workers, seed data beyond optional dev fixtures.

---

## Post-MVP Collection Stubs

When implementing deferred collections, use schemas defined in [LLD.md](LLD.md) §5.8–5.18. No MVP code should import or register these models.

| Collection | Trigger Phase |
|------------|---------------|
| `application_history` | First ATS apply status change |
| `recruiters` | Outreach module |
| `emails` | Outreach module |
| `notifications` | Real-time alerts |
| `analytics` | Aggregated dashboard metrics |
| `prompt_logs` | Prompt A/B versioning |
| `audit_logs` | Security hardening |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial 11 collections |
| 0.2.0 | 2026-07-10 | Expanded to 18 collections; split users/profiles |
| 0.3.1 | 2026-07-10 | Email verification fields on `users` |
| 0.4.2 | 2026-10-08 | `resumes.parse_error` is a user-facing message; internal parser errors stay in logs |
| 0.4.1 | 2026-10-08 | `resumes.parse_progress` and `resumes.parse_stage` |
| 0.4.0 | 2026-10-01 | Added `job_matches` for resume-scoped scores |
