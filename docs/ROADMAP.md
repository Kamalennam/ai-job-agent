# Roadmap — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

---

## Phase 0: Engineering Blueprint (Current)

**Duration**: 2 weeks  
**Status**: 🟡 In Progress

| Deliverable | Status |
|-------------|--------|
| Project scaffold (folders, no logic) | ✅ |
| PROJECT_VISION.md | ✅ |
| PRD.md | ✅ |
| ROADMAP.md | ✅ |
| HLD.md | ✅ |
| LLD.md | ✅ |
| API_SPEC.md | ✅ |
| DATABASE.md | ✅ |
| DEPLOYMENT.md | ✅ |
| SECURITY.md | ✅ |
| AI_PROMPTS.md | ✅ |
| CODING_GUIDELINES.md | ✅ |
| TESTING.md | ✅ |
| Cursor governance rules | ✅ |
| Docker Compose skeleton | ✅ |
| Config YAML files | ✅ |

**Exit Criteria**: All docs reviewed. Cursor rules active. Zero business logic.

---

## Phase 1: Foundation (Weeks 3–5)

**Goal**: Runnable backend + frontend shell with auth.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 1.1 | FastAPI app, MongoDB connection, Beanie models | LLD, DATABASE, DEPLOYMENT |
| 1.2 | JWT auth (register, login, refresh) | API_SPEC, SECURITY |
| 1.3 | React app shell, routing, auth pages | LLD (frontend section) |
| 1.4 | Docker Compose full stack running | DEPLOYMENT, README |

**Milestone**: `make up` → register → login → see empty dashboard.

---

## Phase 2: Resume Pipeline (Weeks 6–8)

**Goal**: Upload, parse, display resumes.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 2.1 | Resume upload API + file storage | API_SPEC, LLD |
| 2.2 | PyMuPDF + pdfplumber parsing | LLD, AI_PROMPTS |
| 2.3 | resume_parser_worker (Celery) | HLD, LLD |
| 2.4 | Resume UI (upload, preview, edit) | LLD (frontend) |
| 2.5 | Embedding generation (Ollama) | AI_PROMPTS, DATABASE |

**Milestone**: Upload PDF → parsed profile visible → embedding stored.

---

## Phase 3: Job Discovery (Weeks 9–11)

**Goal**: Automated job collection from all sources.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 3.1 | Greenhouse + Lever collectors | LLD, configs/job_sources.yaml |
| 3.2 | Ashby + company_sites collectors | LLD |
| 3.3 | LinkedIn + Indeed collectors | LLD, SECURITY |
| 3.4 | Naukri + Wellfound collectors | LLD |
| 3.5 | job_scraper_worker + dedup logic | HLD, DATABASE |
| 3.6 | Job list UI + detail page | LLD (frontend) |

**Milestone**: Scheduler collects jobs hourly → 100+ jobs in DB → visible in UI.

---

## Phase 4: AI Matching (Weeks 12–14)

**Goal**: Intelligent resume-to-job matching.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 4.1 | Embedding similarity search | LLD, DATABASE (indexes) |
| 4.2 | LLM scoring prompt + ai_worker | AI_PROMPTS, HLD |
| 4.3 | job_match_worker (batch) | HLD, LLD |
| 4.4 | Match results UI with explanations | LLD (frontend) |
| 4.5 | User match preferences | PRD, API_SPEC |

**Milestone**: Matches appear with scores and explanations within 30 min of job collection.

---

## Phase 5: Application Automation (Weeks 15–18)

**Goal**: Resume optimization + ATS auto-apply.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 5.1 | Resume optimizer (AI) | AI_PROMPTS, LLD |
| 5.2 | Cover letter generator | AI_PROMPTS, LLD |
| 5.3 | Playwright ATS apply engine | HLD, LLD, TESTING |
| 5.4 | ats_apply_worker | HLD, LLD |
| 5.5 | Application tracking UI | LLD (frontend) |
| 5.6 | Approval queue (semi-auto mode) | PRD, API_SPEC |

**Milestone**: User approves match → system applies → application recorded with screenshot.

---

## Phase 6: Outreach & Analytics (Weeks 19–21)

**Goal**: Recruiter emails + dashboard.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 6.1 | Recruiter discovery | LLD, DATABASE |
| 6.2 | Email generation + sending | AI_PROMPTS, SECURITY |
| 6.3 | Analytics aggregation worker | HLD, DATABASE |
| 6.4 | Dashboard UI (charts, funnel) | LLD (frontend) |
| 6.5 | Notification system | LLD, API_SPEC |

**Milestone**: Full pipeline operational end-to-end with analytics dashboard.

---

## Phase 7: Hardening & Launch (Weeks 22–24)

**Goal**: Production-ready self-hosted release.

| Sprint | Features | Docs to Update |
|--------|----------|----------------|
| 7.1 | Error handling + retry policies | CODING_GUIDELINES |
| 7.2 | Rate limiting + security audit | SECURITY |
| 7.3 | GitHub Actions CI/CD | DEPLOYMENT |
| 7.4 | Prometheus + Grafana (optional) | DEPLOYMENT |
| 7.5 | End-to-end test suite | TESTING |
| 7.6 | Documentation review + v1.0 tag | All docs |

**Milestone**: v1.0.0 release — self-hosted via Docker Compose.

---

## Future (v2+)

| Feature | Priority | Notes |
|---------|----------|-------|
| Interview prep module | P2 | AI-generated Q&A |
| Multi-user SaaS | P2 | Tenant isolation |
| S3 file storage | P2 | Production scale |
| Gmail API integration | P2 | Better deliverability |
| Chrome extension | P3 | Quick-apply from any page |
| Referral module | P3 | Track referral applications |
| Mobile PWA | P3 | Responsive first in v1 |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| ATS sites change form structure | High | Playwright selectors in config; fallback to manual |
| LinkedIn blocks scraping | Medium | Rate limits; public data only; user-provided cookies option |
| Ollama model quality insufficient | Medium | Model swap via config; cloud LLM fallback option |
| Playwright resource usage | Medium | Max 3 concurrent sessions; queue-based |
| Scope creep | High | PRD non-goals enforced; roadmap phases are gates |
