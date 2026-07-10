# Testing Strategy — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

---

## Overview

| Layer | Framework | Location |
|-------|-----------|----------|
| Backend unit | pytest + pytest-asyncio | `backend/app/tests/unit/` |
| Backend integration | pytest + httpx | `backend/app/tests/integration/` |
| Frontend unit | Vitest | `frontend/src/__tests__/` |
| E2E | Playwright | `backend/app/tests/e2e/` |

---

## Coverage Targets

| Layer | Target | Priority |
|-------|--------|----------|
| Services | 80% | P0 |
| API routes | 70% | P0 |
| Repositories | 60% | P1 |
| Workers | 60% | P1 |
| AI layer | 50% | P2 (mocked) |
| Collectors | 40% | P2 (mocked) |
| Frontend components | 50% | P1 |
| Frontend services | 70% | P1 |

---

## Backend Test Structure

```
backend/app/tests/
├── conftest.py              # Fixtures: test DB, test client, mock user
├── unit/
│   ├── test_auth_service.py
│   ├── test_resume_service.py
│   ├── test_job_service.py
│   ├── test_application_service.py
│   ├── test_analytics_service.py
│   └── test_ai_matching.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_resume_api.py
│   ├── test_jobs_api.py
│   ├── test_applications_api.py
│   └── test_health_api.py
└── e2e/
    ├── test_resume_pipeline.py
    └── test_apply_pipeline.py
```

---

## Key Test Fixtures

```python
# conftest.py
@pytest.fixture
async def test_db():
    """MongoDB test database with Beanie init."""
    
@pytest.fixture
async def client(test_db):
    """httpx AsyncClient with FastAPI app."""
    
@pytest.fixture
async def auth_headers(client):
    """Register test user, return auth headers."""
    
@pytest.fixture
def mock_ollama():
    """Mock Ollama responses for AI tests."""
    
@pytest.fixture
def sample_resume_pdf():
    """Path to test resume PDF."""
```

---

## Critical Test Scenarios

### Auth
- Register with valid/invalid data
- Login with correct/wrong password
- Token refresh flow
- Access protected endpoint without token

### Resume Pipeline
- Upload valid PDF → status pending
- Upload invalid file type → 400
- Parse worker processes resume → parsed status
- Embedding generated after parse

### Job Discovery
- Collector returns jobs → stored in DB
- Deduplication prevents duplicates
- TTL index expires old jobs

### Matching
- Embedding similarity returns ranked jobs
- LLM scoring returns 0-100 with explanation
- Below-threshold matches not notified

### ATS Apply
- Playwright fills form (mocked browser)
- Screenshot captured on success
- Application status updated to "applied"
- Retry on failure (3 attempts)

---

## Frontend Tests

```
frontend/src/__tests__/
├── components/
│   ├── ResumeCard.test.tsx
│   ├── JobCard.test.tsx
│   └── MatchScoreBadge.test.tsx
├── services/
│   ├── authService.test.ts
│   └── resumeService.test.ts
└── pages/
    ├── LoginPage.test.tsx
    └── DashboardPage.test.tsx
```

---

## CI Integration

Tests run in GitHub Actions on every PR:

```yaml
# infrastructure/github-actions/ci.yml
- name: Backend tests
  run: pytest backend/app/tests -v --cov=app --cov-report=xml

- name: Frontend tests
  run: npm run test --prefix frontend
```

---

## Mocking Strategy

| Dependency | Mock Method |
|------------|-------------|
| Ollama | `unittest.mock` / `pytest-mock` |
| Playwright | Mock browser context |
| SMTP | `aiosmtplib` mock |
| External scrapers | Fixture HTML files |
| Celery | `celery.contrib.testing` eager mode |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial testing strategy |
