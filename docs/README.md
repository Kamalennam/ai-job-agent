# Documentation Hub — AI Job Agent Engineering Blueprint

This directory is the **single source of truth** for the AI Job Agent project. No code may be written, modified, or deleted without first consulting and updating these documents.

## Blueprint Philosophy

> **Documentation before code. Architecture before implementation. Maintenance over generation.**

This is not a one-page prompt. This Engineering Blueprint (~15,000 words) describes an entire software platform the way a real engineering organization would: vision, requirements, high-level design, low-level design, APIs, database, deployment, security, AI prompts, and coding standards.

Cursor (and all contributors) must **maintain** this project — not generate random code. When asked to "Add Referral Module," the workflow is:

1. Update PRD → 2. Update HLD → 3. Update LLD → 4. Update README → 5. Update API_SPEC → 6. Update Docker/env → 7. Update diagrams → 8. Generate code

## Document Map

### Strategic Layer

| File | Audience | When to Read |
|------|----------|--------------|
| [PROJECT_VISION.md](PROJECT_VISION.md) | Everyone | First — understand why we exist |
| [PRD.md](PRD.md) | PM, Engineers | Before any feature work |
| [ROADMAP.md](ROADMAP.md) | PM, Tech Lead | Sprint planning |

### Architecture Layer

| File | Audience | When to Read |
|------|----------|--------------|
| [LAYER_RESPONSIBILITIES.md](LAYER_RESPONSIBILITIES.md) | All Engineers | **Read first** — one responsibility per folder |
| [HLD.md](HLD.md) | Architects, Senior Engineers | Before system changes |
| [LLD.md](LLD.md) | All Engineers | Before any code change |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Everyone | Visual system overview |

### Implementation Layer

| File | Audience | When to Read |
|------|----------|--------------|
| [API_SPEC.md](API_SPEC.md) | Backend + Frontend | Before API work |
| [DATABASE.md](DATABASE.md) | Backend | Before model/schema changes |
| [AI_PROMPTS.md](AI_PROMPTS.md) | AI/Backend | Before prompt changes |
| [SECURITY.md](SECURITY.md) | All | Before auth/data changes |
| [DEPLOYMENT.md](DEPLOYMENT.md) | DevOps | Before infra changes |
| [LOCAL_DEV.md](LOCAL_DEV.md) | All Engineers | Daily local development setup |
| [TESTING.md](TESTING.md) | QA, Engineers | Before test work |
| [CODING_GUIDELINES.md](CODING_GUIDELINES.md) | All Engineers | Always |

## Change Protocol

Every change follows this checklist:

```
□ PRD updated (if user-facing behavior changes)
□ HLD updated (if architecture/components change)
□ LLD updated (if modules/APIs/collections change)
□ README.md updated (if setup/usage changes)
□ API_SPEC.md updated (if endpoints change)
□ DATABASE.md updated (if collections/indexes change)
□ DEPLOYMENT.md updated (if Docker/infra changes)
□ .env.example updated (if new env vars)
□ ARCHITECTURE diagram updated (if topology changes)
□ CODING_GUIDELINES.md updated (if new patterns introduced)
□ Code generated (only after all above are complete)
```

## Word Count Targets

| Document | Target Words |
|----------|-------------|
| PROJECT_VISION.md | 800 |
| PRD.md | 2,500 |
| ROADMAP.md | 1,200 |
| HLD.md | 4,000 |
| LLD.md | 6,000 |
| API_SPEC.md | 2,000 |
| DATABASE.md | 1,500 |
| DEPLOYMENT.md | 1,200 |
| SECURITY.md | 800 |
| AI_PROMPTS.md | 1,500 |
| CODING_GUIDELINES.md | 1,000 |
| TESTING.md | 800 |
| **Total** | **~23,000** |

## Versioning

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1.0 | 2026-07-10 | Engineering Blueprint | Initial documentation-only release |
| 0.2.0 | 2026-07-10 | Engineering Blueprint | SRP layers, events/, 18 collections, worker rename |
