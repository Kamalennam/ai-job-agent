# AI Prompts — AI Job Agent

**Version**: 0.1.0  
**Last Updated**: 2026-07-10

> Prompt files live in `prompts/` (runtime) and are documented here (blueprint). When prompts change, update BOTH locations.

---

## Prompt Registry

| ID | File | Model | Used By | Purpose |
|----|------|-------|---------|---------|
| P01 | `resume_extraction.md` | llama3.2 | `ai/resume_extraction/` | Extract skills, experience, projects from raw text |
| P02 | `resume_matching.md` | llama3.2 | `ai/resume_matching/` | Score resume against job description |
| P03 | `cover_letter.md` | llama3.2 | `ai/cover_letter/` | Generate personalized cover letter |
| P04 | `recruiter_email.md` | llama3.2 | `ai/recruiter_email/` | Generate recruiter outreach email |
| P05 | `ats_optimizer.md` | llama3.2 | `ai/resume_matching/` | Optimize resume keywords for ATS |
| P06 | `interview_questions.md` | llama3.2 | `ai/interview/` | Generate interview prep Q&A (v2) |

---

## P01: Resume Extraction

**File**: `prompts/resume_extraction.md`

```
You are a resume parsing expert. Extract structured information from the following resume text.

Return ONLY valid JSON with this structure:
{
  "name": "string",
  "email": "string or null",
  "phone": "string or null",
  "skills": ["string"],
  "experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "YYYY-MM or YYYY",
      "end_date": "YYYY-MM or YYYY or null if current",
      "description": "string"
    }
  ],
  "projects": [
    {
      "name": "string",
      "description": "string or null",
      "technologies": ["string"],
      "url": "string or null",
      "start_date": "YYYY-MM or YYYY or null",
      "end_date": "YYYY-MM or YYYY or null"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string or null",
      "start_date": "YYYY",
      "end_date": "YYYY or null"
    }
  ],
  "summary": "string or null"
}

Rules:
- Extract ALL skills mentioned (technical and soft)
- Preserve dates as found in resume
- If a field is not found, use null
- Do not invent information not present in the resume

RESUME TEXT:
{resume_text}
```

---

## P02: Resume Matching

**File**: `prompts/resume_matching.md`

```
You are an expert career matching AI. Score how well this candidate fits the job.

CANDIDATE RESUME:
{resume_summary}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON:
{
  "score": 0-100,
  "strengths": ["string"],
  "gaps": ["string"],
  "recommendation": "apply" | "consider" | "skip",
  "explanation": "2-3 sentence summary"
}

Scoring criteria:
- Skills match (40%): Required skills present?
- Experience level (30%): Years and seniority alignment?
- Domain fit (20%): Industry/role relevance?
- Location/remote (10%): Compatible?

Be honest about gaps. Score below 50 if major requirements are missing.
```

---

## P03: Cover Letter

**File**: `prompts/cover_letter.md`

```
Write a professional cover letter for this job application.

CANDIDATE:
Name: {candidate_name}
Summary: {resume_summary}
Key Skills: {skills}

JOB:
Title: {job_title}
Company: {company_name}
Description: {job_description}

Requirements:
- 3-4 paragraphs, professional but personable tone
- Reference specific skills that match the job
- Mention the company by name
- Do not use generic filler phrases
- Maximum 400 words
- Do not include address/date headers

Return the cover letter text only, no JSON.
```

---

## P04: Recruiter Email

**File**: `prompts/recruiter_email.md`

```
Write a brief, professional outreach email to a recruiter about a job application.

CANDIDATE:
Name: {candidate_name}
Summary: {resume_summary}

RECRUITER:
Name: {recruiter_name}
Title: {recruiter_title}

JOB:
Title: {job_title}
Company: {company_name}

Return ONLY valid JSON:
{
  "subject": "string (max 80 chars)",
  "body": "string (max 200 words, plain text)"
}

Rules:
- Professional but warm tone
- Mention specific qualifications relevant to the role
- Keep it concise — recruiters are busy
- Include a clear call to action
- Do not be overly salesy
```

---

## P05: ATS Optimizer

**File**: `prompts/ats_optimizer.md`

```
Optimize this resume for ATS (Applicant Tracking System) compatibility with this job description.

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON:
{
  "optimized_text": "full resume text with improvements",
  "keywords_added": ["string"],
  "keywords_removed": ["string"],
  "changes_summary": "brief description of changes made"
}

Rules:
- Add relevant keywords from job description naturally
- Do NOT fabricate experience or skills
- Preserve original structure and formatting
- Maximum 15 keywords to add
- Maintain truthfulness — only rephrase existing experience
```

---

## P06: Interview Questions (v2)

**File**: `prompts/interview_questions.md`

```
Generate likely interview questions for this job based on the candidate's profile.

CANDIDATE SKILLS: {skills}
JOB DESCRIPTION: {job_description}

Return ONLY valid JSON:
{
  "technical": [{"question": "string", "hint": "string"}],
  "behavioral": [{"question": "string", "hint": "string"}],
  "company_specific": [{"question": "string", "hint": "string"}]
}

Generate 5 questions per category.
```

---

## Prompt Loading

```python
# backend/app/ai/prompts/loader.py
def load_prompt(name: str, **kwargs) -> str:
    template = Path(f"prompts/{name}.md").read_text()
    return template.format(**kwargs)
```

---

## Model Configuration

See `configs/ai.yaml`:

```yaml
generation:
  model: llama3.2
  temperature: 0.3        # Low for structured extraction
  max_tokens: 4096

matching:
  model: llama3.2
  temperature: 0.5        # Moderate for scoring variety

creative:
  model: llama3.2
  temperature: 0.7        # Higher for cover letters/emails
  max_tokens: 2048
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-07-10 | Initial prompt registry |
