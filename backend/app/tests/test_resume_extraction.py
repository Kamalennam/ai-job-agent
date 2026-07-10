import json

from app.ai.resume_extraction.extract import build_prompt, parse_json_response
from app.ai.resume_extraction.schemas import ResumeExtractionResult


def test_parse_json_response_from_fenced_block():
    raw = """```json
{
  "name": "Jane Developer",
  "email": "jane@example.com",
  "phone": null,
  "skills": ["Python"],
  "experience": [],
  "projects": [{"name": "AI Job Agent", "description": "Demo", "technologies": ["FastAPI"]}],
  "education": [],
  "summary": "Engineer"
}
```"""
    payload = parse_json_response(raw)
    result = ResumeExtractionResult.model_validate(payload)
    assert result.name == "Jane Developer"
    assert result.projects[0].name == "AI Job Agent"


def test_build_prompt_includes_resume_text():
    prompt = build_prompt("Sample resume body")
    assert "Sample resume body" in prompt
    assert "{resume_text}" not in prompt


def test_resume_extraction_schema_accepts_full_payload():
    payload = json.loads(
        """
        {
          "name": "Alex",
          "email": "alex@example.com",
          "phone": "+1 555 000 1111",
          "skills": ["Python", "React"],
          "experience": [
            {
              "company": "Acme",
              "title": "Engineer",
              "start_date": "2020",
              "end_date": null,
              "description": "Built APIs",
              "location": "Remote"
            }
          ],
          "projects": [
            {
              "name": "Side Project",
              "description": "Demo app",
              "technologies": ["FastAPI"],
              "url": null,
              "start_date": "2024",
              "end_date": null
            }
          ],
          "education": [
            {
              "institution": "State U",
              "degree": "BS",
              "field": "CS",
              "start_date": "2014",
              "end_date": "2018"
            }
          ],
          "summary": "Backend engineer"
        }
        """
    )
    result = ResumeExtractionResult.model_validate(payload)
    assert len(result.skills) == 2
    assert len(result.experience) == 1
    assert len(result.projects) == 1
