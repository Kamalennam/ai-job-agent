# Product Requirements Document (PRD) — AI Job Agent

**Version**: 0.1.0  
**Status**: Draft — Blueprint Phase  
**Last Updated**: 2026-07-10

---

## 1. Overview

AI Job Agent is an AI-powered job search automation platform. This PRD defines functional requirements, user stories, acceptance criteria, and feature scope for v1.0.

## 2. Goals

| ID | Goal | Priority |
|----|------|----------|
| G1 | Parse resumes into structured, searchable profiles | P0 |
| G2 | Discover jobs from 8+ external sources automatically | P0 |
| G3 | AI-match candidates to jobs with explainable scores | P0 |
| G4 | Optimize resumes per job for ATS compatibility | P0 |
| G5 | Automate ATS job applications via browser | P0 |
| G6 | Generate personalized cover letters | P1 |
| G7 | Discover recruiters and draft outreach emails | P1 |
| G8 | Provide analytics dashboard for entire pipeline | P1 |
| G9 | Send notifications for matches and application status | P1 |
| G10 | Support user preferences and automation settings | P0 |

## 3. Non-Goals (v1)

- Multi-user SaaS tenancy
- Mobile native apps
- Interview preparation module
- Paid job board API integrations
- Social/collaborative features
- Video resume analysis

## 4. User Personas

### Persona A: Active Job Seeker (Primary)

- **Name**: Alex, 28, Software Engineer
- **Pain**: Spends 15+ hours/week manually searching and applying
- **Need**: Upload resume once, let the system find and apply to relevant jobs
- **Control**: Wants to review matches before auto-apply

### Persona B: Passive Job Seeker

- **Name**: Jordan, 35, Senior Developer
- **Pain**: Only wants top 5% matches, not spam
- **Need**: High-quality matches with score explanations
- **Control**: Notification-only mode, manual apply

## 5. Feature Requirements

### 5.1 Authentication & User Management

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| AUTH-01 | User registration with email/password | JWT issued, user record in MongoDB |
| AUTH-02 | Login with email/password | Access + refresh token returned |
| AUTH-03 | Token refresh | New access token without re-login |
| AUTH-04 | Password reset via email | Reset link expires in 1 hour |
| AUTH-05 | User profile management | Name, email, preferences editable |

### 5.2 Resume Management

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| RES-01 | Upload PDF/DOCX resume | File stored, parse job queued |
| RES-02 | Parse resume to structured JSON | Name, email, skills, experience, education extracted |
| RES-03 | Multiple resume versions | User can maintain primary + variants |
| RES-04 | Resume preview | Rendered parsed view in UI |
| RES-05 | Manual edit parsed fields | User corrections saved and re-embedded |
| RES-06 | Resume embedding generation | Vector stored for similarity matching |

### 5.3 Job Discovery

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| JOB-01 | Collect from Greenhouse boards | Jobs stored with source metadata |
| JOB-02 | Collect from Lever boards | Jobs stored with source metadata |
| JOB-03 | Collect from Ashby boards | Jobs stored with source metadata |
| JOB-04 | Collect from company career sites | Configurable per company |
| JOB-05 | Collect from LinkedIn (public) | Rate-limited, stored |
| JOB-06 | Collect from Indeed | Rate-limited, stored |
| JOB-07 | Collect from Naukri | Rate-limited, stored |
| JOB-08 | Collect from Wellfound | Rate-limited, stored |
| JOB-09 | Deduplicate jobs across sources | Fuzzy match on title+company+location |
| JOB-10 | Job detail view | Full description, requirements, apply URL |

### 5.4 AI Matching

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| MAT-01 | Score resume against job description | 0-100 score with breakdown |
| MAT-02 | Embedding similarity search | Top-N jobs by vector distance |
| MAT-03 | LLM qualitative assessment | Strengths, gaps, recommendation |
| MAT-04 | Configurable match threshold | User sets minimum score |
| MAT-05 | Match explanations | Human-readable reason for score |
| MAT-06 | Batch matching on schedule | Celery worker runs every 30 min |

### 5.5 Resume Optimization

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| OPT-01 | Tailor resume keywords to JD | ATS keyword density improved |
| OPT-02 | Generate optimized PDF | Downloadable optimized version |
| OPT-03 | Show diff (original vs optimized) | Side-by-side in UI |
| OPT-04 | Per-job optimization | One optimized version per application |

### 5.6 Application Management

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| APP-01 | Manual apply tracking | User marks job as applied |
| APP-02 | Auto-apply via Playwright | Form filled and submitted |
| APP-03 | Application status tracking | Applied, Interview, Rejected, Offer |
| APP-04 | Cover letter generation | AI-generated per job |
| APP-05 | Application history | Full timeline per job |
| APP-06 | Auto-apply guardrails | User approval queue before submit |

### 5.7 Recruiter Outreach

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| REC-01 | Discover recruiter from job posting | Name, title, email if available |
| REC-02 | Generate outreach email | Personalized, professional tone |
| REC-03 | Send email via SMTP | Delivery confirmation |
| REC-04 | Track email status | Sent, Opened (if trackable), Replied |

### 5.8 Analytics

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| ANA-01 | Applications per week chart | Time-series data |
| ANA-02 | Match score distribution | Histogram |
| ANA-03 | Source breakdown | Jobs by collector source |
| ANA-04 | Response rate tracking | Applied → Interview conversion |
| ANA-05 | Pipeline funnel | Discovered → Matched → Applied → Response |

### 5.9 Notifications

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| NOT-01 | In-app notifications | Bell icon with unread count |
| NOT-02 | Email notifications | Configurable per event type |
| NOT-03 | New high-score match alert | Triggered when score > threshold |
| NOT-04 | Application status change | Triggered on status update |

### 5.10 Settings & Automation

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| SET-01 | Job search preferences | Location, remote, salary, titles |
| SET-02 | Automation mode toggle | Manual / Semi-auto / Full-auto |
| SET-03 | Collector source enable/disable | Per-source toggle |
| SET-04 | AI model selection | Ollama model picker |
| SET-05 | Schedule configuration | View/edit cron schedules |

## 6. User Stories

### Epic 1: Onboarding

```
AS A new user
I WANT TO register and upload my resume
SO THAT the system can understand my profile and start finding jobs
```

**Acceptance**: Registration → Upload → Parse completes within 60s → Dashboard shows parsed profile.

### Epic 2: Job Discovery

```
AS A job seeker
I WANT the system to automatically find relevant jobs
SO THAT I don't spend hours searching job boards
```

**Acceptance**: Within 1 hour of onboarding, ≥ 10 jobs discovered matching user's title preferences.

### Epic 3: Intelligent Matching

```
AS A job seeker
I WANT to see which jobs I'm best suited for with explanations
SO THAT I can focus on high-probability applications
```

**Acceptance**: Match list shows score, strengths, gaps, and recommended action.

### Epic 4: Automated Application

```
AS A job seeker
I WANT the system to apply on my behalf
SO THAT I can apply to more jobs without manual form filling
```

**Acceptance**: Playwright worker fills and submits ATS form; application record created with timestamp and screenshot.

### Epic 5: Analytics

```
AS A job seeker
I WANT a dashboard showing my job search progress
SO THAT I can measure effectiveness and adjust strategy
```

**Acceptance**: Dashboard shows funnel, weekly applications, response rate.

## 7. Pipeline Requirements

Every feature maps to a defined pipeline (see HLD.md):

| Pipeline | Trigger | Output |
|----------|---------|--------|
| User Registration | POST /auth/register | User + JWT |
| Resume Upload | POST /resumes/upload | Stored file + parse task |
| Resume Parsing | Celery: resume_parser_worker | ParsedResume document |
| Embedding | Celery: ai_worker (embed task) | Vector in MongoDB |
| Job Discovery | Scheduler: hourly | Job documents |
| AI Matching | Scheduler: every 30 min | Match scores |
| Resume Selection | User action or auto | Selected resume version |
| ATS Apply | Celery: ats_apply_worker | Application record |
| Recruiter Discovery | Post-apply or manual | Recruiter document |
| Email Generation | Celery: email_worker | Draft email |
| Analytics | Scheduler: hourly | Analytics aggregates |
| Notification | Event-driven | In-app + email notification |

## 8. Constraints

- **Privacy**: All AI inference runs locally via Ollama by default
- **Rate limits**: External scraping respects robots.txt and rate limits
- **Storage**: Resumes stored on local filesystem (configurable to S3 in v2)
- **Concurrency**: Max 3 parallel Playwright sessions
- **Retention**: Job data retained 90 days; applications retained indefinitely

## 9. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Gmail API vs SMTP for email? | Backend Lead | SMTP v1, Gmail API v2 |
| 2 | LinkedIn scraping legal constraints? | Legal/Tech | Public listings only |
| 3 | S3 storage for production? | DevOps | Deferred to v2 |

## 10. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial PRD from Engineering Blueprint |
