# Security — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

---

## Authentication

### JWT Strategy

| Token | Lifetime | Storage (Frontend) | Storage (Backend) |
|-------|----------|-------------------|-------------------|
| Access Token | 30 minutes | Memory (Zustand) | — |
| Refresh Token | 7 days | HttpOnly cookie (preferred) or secure storage | Redis blacklist on logout |

### Password Requirements

- Minimum 8 characters
- Hashed with bcrypt (cost factor 12)
- Never logged or returned in API responses

### Token Refresh Flow

1. Access token expires → frontend interceptor catches 401
2. Frontend calls `POST /auth/refresh` with refresh token
3. New access + refresh tokens issued
4. Original request retried

---

## Authorization

- All API endpoints require valid JWT except `/auth/*` and `/health/*`
- Users can only access their own data (user_id from JWT matched against resource)
- No admin role in v1 (single-user self-hosted)

---

## Data Privacy

| Data | Storage | External Exposure |
|------|---------|-------------------|
| Resumes | Local filesystem | Never sent to external APIs |
| Parsed resume data | MongoDB | Never sent to external APIs |
| AI inference | Ollama (local) | Stays on user's infrastructure |
| Job listings | MongoDB | Public data (scraped) |
| Email credentials | `.env` only | SMTP connection only |

---

## Rate Limiting

Implemented via Redis counters in `core/dependencies.py`:

| Endpoint Group | Limit | Window |
|---------------|-------|--------|
| Auth endpoints | 10 requests | 1 minute |
| File upload | 5 requests | 1 minute |
| General API | 60 requests | 1 minute |
| Manual job collect | 2 requests | 1 hour |

Response on limit: `429 Too Many Requests` with `Retry-After` header.

---

## Input Validation

- All request bodies validated via Pydantic schemas
- File uploads: type check (MIME), size limit (10MB), extension whitelist
- SQL/NoSQL injection: Beanie ODM parameterized queries only
- XSS: React auto-escaping; no `dangerouslySetInnerHTML`

---

## CORS

```python
CORS_ORIGINS = env.list("CORS_ORIGINS")  # Explicit whitelist only
```

Development: `http://localhost:5173`  
Production: `https://yourdomain.com`

---

## Secrets Management

| Secret | Storage | Rotation |
|--------|---------|----------|
| `APP_SECRET_KEY` | `.env` | On deploy |
| `JWT_SECRET_KEY` | `.env` | Quarterly |
| `MONGODB_URI` | `.env` | On credential change |
| `SMTP_PASSWORD` | `.env` | On credential change |

**Rules:**
- Never commit `.env` to git
- `.env.example` contains placeholders only
- Production secrets via environment variables or secrets manager (v2)

---

## File Security

- Uploads stored at `{UPLOAD_DIR}/{user_id}/{filename}`
- Downloads require auth + ownership check
- No direct filesystem access from API (always through service layer)
- Temp files cleaned by `cleanup_worker` weekly

---

## Playwright Security

- Runs in isolated Docker container
- No access to host filesystem except `playwright-data` volume
- Browser contexts destroyed after each apply
- Screenshots stored with user-scoped paths

---

## Scraping Ethics

- Respect `robots.txt` for all collectors
- Rate limiting per source (configurable in `job_sources.yaml`)
- User-agent identifies as bot
- Public data only (no authenticated scraping in v1)

---

## Security Checklist (Pre-Launch)

- [ ] Change all default secrets in `.env`
- [ ] Enable HTTPS (Nginx + Let's Encrypt)
- [ ] Verify CORS origins are restrictive
- [ ] Confirm rate limiting is active
- [ ] Audit file upload validation
- [ ] Verify JWT expiration times
- [ ] Test unauthorized access to other users' data
- [ ] Confirm Ollama is not exposed publicly

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial security spec |
