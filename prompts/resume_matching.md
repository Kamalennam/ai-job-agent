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
