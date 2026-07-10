# Project Vision — AI Job Agent

## North Star

**Help every job seeker apply to the right jobs, with the right resume, at the right time — automatically.**

AI Job Agent is not a job board. It is an **intelligent automation layer** that sits between a candidate and the entire job market, handling the repetitive, time-consuming work of discovery, matching, optimization, application, and follow-up.

## The Problem

Modern job searching is broken:

- **Volume**: Thousands of relevant jobs exist; manually finding them is impossible.
- **ATS friction**: 75%+ of resumes are rejected by Applicant Tracking Systems before a human sees them.
- **Repetition**: Applying to 50+ jobs means 50+ cover letters, 50+ form fills, 50+ follow-ups.
- **Signal loss**: Candidates don't know which jobs they're actually qualified for.
- **Recruiter gap**: Finding and contacting the right recruiter is manual and awkward.

## The Solution

An end-to-end pipeline that:

1. Understands the candidate (parsed resume + preferences)
2. Continuously discovers new jobs from 8+ sources
3. Scores and ranks matches using AI
4. Tailors resumes and cover letters per application
5. Submits applications via browser automation
6. Identifies recruiters and drafts outreach
7. Tracks everything in a unified analytics dashboard

## Core Principles

### 1. Documentation-First Engineering

Every architectural decision is written down before code exists. The Engineering Blueprint is not optional — it is the contract between product, engineering, and AI agents.

### 2. Local-First AI

We use **Ollama** for local LLM inference. No candidate resume data leaves the user's infrastructure unless explicitly configured. Privacy is a feature, not an afterthought.

### 3. Pipeline Architecture

Every user action triggers a **defined pipeline** with clear inputs, outputs, workers, and failure modes. No ad-hoc background tasks.

### 4. Separation of Concerns

- **API layer** handles HTTP only
- **Service layer** contains business logic
- **Repository layer** handles data access
- **Worker layer** handles async/background processing
- **Collector layer** handles external job source scraping
- **AI layer** handles all LLM interactions

### 5. Maintainability Over Speed

We optimize for long-term maintainability. Cursor maintains this project; it does not randomly generate code. Every change updates documentation.

## Success Criteria

| Metric | Target (6 months post-launch) |
|--------|-------------------------------|
| Resume parse accuracy | ≥ 95% field extraction |
| Job match relevance (user-rated) | ≥ 80% "relevant" |
| ATS application success rate | ≥ 90% form submission |
| Time saved per user per week | ≥ 10 hours |
| System uptime | ≥ 99.5% |
| API p95 latency | < 200ms (non-AI endpoints) |

## Non-Goals (v1)

- **Not a social network** — no candidate-to-candidate features
- **Not a job board UI** — we aggregate, not host listings
- **Not interview coaching** (v1) — deferred to v2
- **Not multi-tenant SaaS** (v1) — single-user/self-hosted first
- **Not mobile app** (v1) — responsive web only
- **Not paid job APIs** — free scraping/collecting only in v1

## Target User

**Primary**: Software engineers and tech professionals actively job searching who want to automate the tedious parts while retaining control over what gets applied to.

**Secondary**: Career coaches who manage multiple candidates (v2).

## Competitive Differentiation

| Feature | LinkedIn Easy Apply | Jobright | Huntr | **AI Job Agent** |
|---------|-------------------|----------|-------|------------------|
| Multi-source job discovery | ❌ | Partial | ❌ | ✅ 8+ sources |
| AI resume optimization | ❌ | ✅ | ❌ | ✅ Per-job |
| ATS browser automation | ❌ | ❌ | ❌ | ✅ Playwright |
| Recruiter email generation | ❌ | ❌ | ❌ | ✅ |
| Local AI (privacy) | ❌ | ❌ | ❌ | ✅ Ollama |
| Self-hosted | ❌ | ❌ | ❌ | ✅ Docker |
| Full analytics pipeline | ❌ | Partial | Partial | ✅ |

## Engineering Identity

When Cursor (or any engineer) works on this project, the mindset is:

> *"I am the Lead Software Architect of AI Job Agent. I do not write code until the blueprint allows it. I do not create files outside the defined structure. I update documentation with every change."*

This is how real engineering teams work. This project is built to be **maintained**, not **generated**.
