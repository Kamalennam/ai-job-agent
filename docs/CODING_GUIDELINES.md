# Coding Guidelines — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

---

## Golden Rules

1. **Never create files outside the architecture** defined in LLD.md
2. **Never rename folders** without updating LLD.md and HLD.md
3. **Never mix responsibilities** — API layer has no business logic, services have no HTTP
4. **Never duplicate models** — one Beanie model per collection, one Pydantic schema per DTO
5. **Always update documentation** when changing architecture, APIs, or schemas

---

## Backend (Python)

### Style

- Python 3.11+
- Formatter: Ruff (line length 100)
- Type hints on all function signatures
- Async everywhere (FastAPI, Beanie, Motor)

### Layer Rules

```
api/v1/     → HTTP only. Calls service. Returns schema.
services/   → Business logic. Calls repository + workers.
repositories/ → DB access only. Returns Beanie documents.
models/     → Beanie Document classes only.
schemas/    → Pydantic request/response DTOs only.
workers/    → Celery tasks. Calls services.
ai/         → LLM calls only. No direct DB access.
collectors/ → External scraping only. Returns RawJob dataclass.
```

### Naming

| Entity | Convention | Example |
|--------|-----------|---------|
| File | snake_case | `resume_service.py` |
| Class | PascalCase | `ResumeService` |
| Function | snake_case | `parse_resume` |
| Constant | UPPER_SNAKE | `MAX_FILE_SIZE` |
| Celery task | snake_case | `parse_resume` |
| Queue | lowercase | `resume` |

### Error Handling

```python
# Use custom exceptions from core/exceptions.py
from app.core.exceptions import NotFoundError, ValidationError

# In service:
if not resume:
    raise NotFoundError("Resume", resume_id)

# Never bare except:
except Exception as e:
    logger.error("Parse failed", resume_id=resume_id, error=str(e))
    raise ResumeParseError(resume_id) from e
```

### Logging

```python
from app.core.logger import logger

logger.info("Resume parsed", resume_id=resume_id, duration_ms=elapsed)
```

---

## Frontend (TypeScript/React)

### Style

- TypeScript strict mode
- Functional components only
- Tailwind CSS for styling
- Zustand for global state

### Naming

| Entity | Convention | Example |
|--------|-----------|---------|
| Component file | PascalCase.tsx | `ResumeCard.tsx` |
| Hook file | camelCase.ts | `useResumes.ts` |
| Service file | camelCase.ts | `resumeService.ts` |
| Type/Interface | PascalCase | `ParsedResume` |

### Component Structure

```tsx
// Props interface above component
interface ResumeCardProps {
  resume: Resume;
  onSelect: (id: string) => void;
}

export function ResumeCard({ resume, onSelect }: ResumeCardProps) {
  // hooks first
  // handlers
  // render
}
```

### API Calls

- All API calls through `services/` — never raw fetch in components
- Axios instance in `services/api.ts` with auth interceptor

---

## Git Conventions

### Branch Naming

```
feature/resume-upload
fix/ats-form-detection
docs/update-api-spec
```

### Commit Messages

```
feat: add resume upload endpoint
fix: handle pdfplumber fallback parsing
docs: update LLD with referral module
chore: update docker-compose for celery scaling
```

---

## Testing Standards

- Backend: pytest + pytest-asyncio
- Frontend: Vitest + React Testing Library
- Minimum coverage: 70% for services, 50% for API routes
- See [TESTING.md](TESTING.md)

---

## Documentation Updates

When making any change, update the relevant docs:

| Change Type | Documents to Update |
|-------------|-------------------|
| New API endpoint | LLD.md, API_SPEC.md |
| New collection | LLD.md, DATABASE.md |
| New worker/queue | HLD.md, LLD.md |
| New frontend page | LLD.md |
| New env var | .env.example, DEPLOYMENT.md, LLD.md |
| New prompt | AI_PROMPTS.md, prompts/ |
| Architecture change | HLD.md, ARCHITECTURE.md |
| New feature | PRD.md, ROADMAP.md |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial coding guidelines |
