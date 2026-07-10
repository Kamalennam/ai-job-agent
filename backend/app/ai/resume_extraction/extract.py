import json
import re

from pydantic import ValidationError

from app.ai.ollama_client import OllamaError, generate_json
from app.ai.resume_extraction.schemas import ResumeExtractionResult
from app.config import get_settings

PROMPT_FILE = "resume_extraction.md"
PROMPT_VERSION = "resume_extraction-v1.1"


def load_prompt_template() -> str:
    settings = get_settings()
    prompt_path = settings.resolved_prompts_dir / PROMPT_FILE
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def build_prompt(resume_text: str) -> str:
    template = load_prompt_template()
    return template.replace("{resume_text}", resume_text)


def parse_json_response(raw: str) -> dict:
    text = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()
    return json.loads(text)


async def extract_structured_resume(resume_text: str) -> ResumeExtractionResult:
    """Call Ollama to extract skills, experience, and projects from resume text."""
    prompt = build_prompt(resume_text)
    raw_response = await generate_json(prompt)

    try:
        payload = parse_json_response(raw_response)
        return ResumeExtractionResult.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise OllamaError(f"Failed to parse Ollama JSON output: {exc}") from exc
