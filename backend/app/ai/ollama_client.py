import httpx
from loguru import logger

from app.config import get_settings


class OllamaError(Exception):
    pass


async def generate_json(
    prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.3,
    timeout_seconds: int = 120,
) -> str:
    settings = get_settings()
    payload = {
        "model": model or settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
    }

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Ollama request failed: {}", exc)
            raise OllamaError(f"Ollama request failed: {exc}") from exc

    data = response.json()
    content = data.get("response", "")
    if not content.strip():
        raise OllamaError("Ollama returned an empty response")
    return content
