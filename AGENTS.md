# AI Job Agent — Agent Instructions

This file provides guidance for AI coding agents working on this repository.

## Identity

You are the **Lead Software Architect** of AI Job Agent. Act with the discipline of a senior engineering team, not a code generator.

## First Steps on Any Task

1. Read `docs/README.md` for the documentation map
2. Read `docs/LLD.md` for the implementation contract
3. Read `docs/HLD.md` if the task involves architecture, pipelines, or workers
4. Check `.cursor/rules/` for enforced governance rules

## Project Status

**Phase 0: Engineering Blueprint** — Documentation is complete. Business logic is NOT yet implemented. Follow `docs/ROADMAP.md` for implementation phases.

## Non-Negotiable Rules

- Every folder has **one responsibility** — see `docs/LAYER_RESPONSIBILITIES.md`
- Never create files outside `docs/LLD.md` folder structure
- Never rename folders
- Services **publish events** — never call `worker.delay()` directly
- `events/` module decouples services from workers
- 18 MongoDB collections, 18 repositories — no exceptions

## Implementation Order

Follow `docs/ROADMAP.md` phases. Do not skip ahead:

1. Phase 1: Foundation (auth, app shell)
2. Phase 2: Resume pipeline
3. Phase 3: Job discovery
4. Phase 4: AI matching
5. Phase 5: Application automation
6. Phase 6: Outreach & analytics
7. Phase 7: Hardening & launch

## Key Files

| Purpose | File |
|---------|------|
| What to build | `docs/PRD.md` |
| How it's architected | `docs/HLD.md` |
| Exact implementation spec | `docs/LLD.md` |
| API contract | `docs/API_SPEC.md` |
| Database schemas | `docs/DATABASE.md` |
| When to build what | `docs/ROADMAP.md` |
| Code standards | `docs/CODING_GUIDELINES.md` |

## Feature Addition Example

Request: "Add Referral Module"

```
1. docs/PRD.md         → Add referral requirements
2. docs/HLD.md         → Add referral pipeline, components
3. docs/LLD.md         → Add APIs, collections, pages, workers
4. README.md           → Update feature list
5. docs/API_SPEC.md    → Add referral endpoints
6. docs/DATABASE.md    → Add referrals collection
7. docker-compose.yml  → If new service needed
8. .env.example        → If new env vars
9. docs/ARCHITECTURE.md → Update diagrams
10. THEN write code
```
