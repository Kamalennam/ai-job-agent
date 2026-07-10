# API Specification — AI Job Agent

**Version**: 0.2.0  
**Base URL**: `/api/v1`  
**OpenAPI**: Auto-generated at `/docs` (Swagger UI) when backend runs  
**Last Updated**: 2026-07-10

> This document mirrors the OpenAPI spec. When endpoints change, update this file AND verify `/docs` reflects changes.

---

## Authentication

All endpoints except `/auth/*` and `/health/*` require:

```
Authorization: Bearer <access_token>
```

Token refresh: `POST /auth/refresh` with `{ "refresh_token": "..." }`.

---

## Error Envelope

All errors return:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

| HTTP Status | Code Examples |
|-------------|---------------|
| 400 | `VALIDATION_ERROR`, `INVALID_FILE_TYPE` |
| 401 | `UNAUTHORIZED`, `TOKEN_EXPIRED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 409 | `DUPLICATE_EMAIL`, `ALREADY_APPLIED` |
| 422 | `RESUME_PARSE_FAILED` |
| 429 | `RATE_LIMIT_EXCEEDED` |
| 500 | `INTERNAL_ERROR` |

---

## Endpoints

### Auth

#### POST /auth/register

Register a new user. Sends a verification email. **Does not return tokens** until email is verified.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "User Name"
}
```

**Response 201:**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "user@example.com"
}
```

**Errors:** `409 DUPLICATE_EMAIL`

#### POST /auth/verify-email

Verify email with token from registration email.

**Request:**
```json
{
  "token": "url-safe-token-from-email"
}
```

**Response 200:**
```json
{
  "message": "Email verified successfully. You can now sign in."
}
```

#### GET /auth/verify-email?token={token}

Same as POST — used when user clicks the link in the verification email.

#### POST /auth/resend-verification

Resend verification email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response 200:**
```json
{
  "message": "If an account exists, a verification email has been sent."
}
```

#### POST /auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "opaque-refresh-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:** `401 UNAUTHORIZED`, `403 EMAIL_NOT_VERIFIED`

#### POST /auth/refresh

**Request:**
```json
{
  "refresh_token": "opaque-refresh-token"
}
```

**Response 200:** New `access_token` + `refresh_token` (rotation — old refresh token revoked).

#### POST /auth/logout

**Auth:** Required

**Response 200:**
```json
{
  "message": "Logged out successfully"
}
```

Revokes all active refresh token sessions for the user.

---

### Resumes

#### POST /resumes/upload

Upload a resume file. Triggers async parsing.

**Request:** `multipart/form-data`
- `file`: PDF, DOC, or DOCX (max 10MB)
- `is_primary`: boolean (optional, default false)

**Response 201:**
```json
{
  "id": "665a1b2c3d4e5f678901234",
  "filename": "alex_resume.pdf",
  "status": "pending",
  "created_at": "2026-07-10T12:00:00Z"
}
```

#### GET /resumes

**Query:** `page=1&page_size=20`

**Response 200:**
```json
{
  "items": [
    {
      "id": "665a1b2c3d4e5f678901234",
      "filename": "alex_resume.pdf",
      "status": "parsed",
      "is_primary": true,
      "created_at": "2026-07-10T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

#### GET /resumes/{id}

**Response 200:**
```json
{
  "id": "665a1b2c3d4e5f678901234",
  "filename": "alex_resume.pdf",
  "status": "parsed",
  "parsed_resume": {
    "name": "User Name",
    "email": "auser@example.com",
    "skills": ["Python", "FastAPI", "React"],
    "experience": [
      {
        "company": "TechCorp",
        "title": "Senior Engineer",
        "start_date": "2022-01",
        "end_date": null,
        "description": "Built microservices..."
      }
    ],
    "education": [
      {
        "institution": "MIT",
        "degree": "BS",
        "field": "Computer Science",
        "start_date": "2016",
        "end_date": "2020"
      }
    ],
    "summary": "Full-stack engineer with 6 years..."
  },
  "created_at": "2026-07-10T12:00:00Z"
}
```

---

### Jobs

#### GET /jobs

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `query` | string | Full-text search |
| `location` | string | Location filter |
| `remote` | boolean | Remote only |
| `source` | string | Collector source |
| `page` | int | Page number (default 1) |
| `page_size` | int | Items per page (default 20, max 100) |

**Response 200:**
```json
{
  "items": [
    {
      "id": "665b2c3d4e5f6789012345",
      "title": "Senior Python Developer",
      "company": "TechCorp",
      "location": "Remote",
      "source": "greenhouse",
      "posted_at": "2026-07-09T08:00:00Z",
      "apply_url": "https://boards.greenhouse.io/techcorp/jobs/123"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

#### POST /jobs/collect

Trigger manual job collection.

**Request:**
```json
{
  "sources": ["greenhouse", "lever"]
}
```

**Response 202:**
```json
{
  "message": "Job collection started for 2 sources"
}
```

---

### Applications

#### GET /applications

**Query:** `status=matched&min_score=70&page=1&page_size=20`

**Response 200:**
```json
{
  "items": [
    {
      "id": "665c3d4e5f67890123456",
      "job_id": "665b2c3d4e5f6789012345",
      "resume_id": "665a1b2c3d4e5f678901234",
      "status": "matched",
      "match_score": 87.5,
      "created_at": "2026-07-10T14:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

#### POST /applications/{id}/apply

Trigger ATS auto-apply. Requires `semi_auto` or `full_auto` mode (or manual approval).

**Response 202:**
```json
{
  "id": "665c3d4e5f67890123456",
  "status": "applying",
  "message": "Application submitted to ATS worker"
}
```

#### GET /applications/{id}/cover-letter

**Response 200:**
```json
{
  "content": "Dear Hiring Manager,\n\nI am excited to apply...",
  "generated_at": "2026-07-10T15:00:00Z"
}
```

---

### Analytics

#### GET /analytics/overview

**Query:** `start_date=2026-07-01&end_date=2026-07-10`

**Response 200:**
```json
{
  "total_jobs": 1250,
  "total_matches": 85,
  "total_applications": 32,
  "response_rate": 0.125
}
```

#### GET /analytics/funnel

**Response 200:**
```json
{
  "discovered": 1250,
  "matched": 85,
  "selected": 45,
  "applied": 32,
  "response": 4
}
```

---

### Dashboard

#### GET /dashboard

Aggregated dashboard data (single call for frontend).

**Response 200:**
```json
{
  "overview": {
    "total_jobs": 1250,
    "total_matches": 85,
    "total_applications": 32,
    "response_rate": 0.125
  },
  "recent_matches": [],
  "recent_applications": [],
  "notifications_count": 3
}
```

---

### Settings

#### GET /settings

**Response 200:**
```json
{
  "automation_mode": "semi_auto",
  "match_threshold": 70.0,
  "preferred_locations": ["Remote", "San Francisco"],
  "preferred_titles": ["Senior Engineer", "Staff Engineer"],
  "remote_only": false,
  "enabled_sources": ["greenhouse", "lever", "linkedin"],
  "email_notifications": true,
  "ai_model": "llama3.2"
}
```

#### PUT /settings

**Request:** Partial update of any settings field.

---

### Health

#### GET /health/live

**Response 200:** `{ "status": "alive" }`

#### GET /health/ready

**Response 200:**
```json
{
  "status": "ready",
  "checks": {
    "mongodb": "ok",
    "redis": "ok",
    "ollama": "ok"
  }
}
```

---

## Rate Limits

| Endpoint Group | Limit |
|---------------|-------|
| Auth | 10 req/min |
| Upload | 5 req/min |
| General API | 60 req/min |
| Collect (manual) | 2 req/hour |

---

## Webhooks (v2)

Not in v1. Planned for external integrations.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial API spec |
