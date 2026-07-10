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
      "start_date": "YYYY-MM or YYYY or null",
      "end_date": "YYYY-MM or YYYY or null if current",
      "description": "string or null",
      "location": "string or null"
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
      "degree": "string or null",
      "field": "string or null",
      "start_date": "YYYY or null",
      "end_date": "YYYY or null"
    }
  ],
  "summary": "string or null"
}

Rules:
- Extract ALL skills mentioned (technical and soft)
- Extract ALL work experience entries with company, title, and dates when present
- Extract ALL projects (personal, open source, academic, or professional side projects)
- Preserve dates as found in the resume
- If a field is not found, use null or an empty array
- Do not invent information not present in the resume

RESUME TEXT:
{resume_text}
