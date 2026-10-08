import json
from collections.abc import Awaitable, Callable

import httpx
from loguru import logger

from app.config import get_settings

TextProgress = Callable[[int], Awaitable[None]]


class OllamaError(Exception):
    pass


def consume_stream_line(parts: list[str], line: str) -> tuple[int, bool]:
    """Append one Ollama NDJSON line. Returns characters added and whether generation finished."""
    if not line.strip():
        return 0, False
    event = json.loads(line)
    piece = event.get("response") or ""
    if piece:
        parts.append(piece)
    return len(piece), bool(event.get("done"))


async def generate_json(
    prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.3,
    timeout_seconds: int = 120,
    on_text: TextProgress | None = None,
) -> str:
    settings = get_settings()
    payload = {
        "model": model or settings.ollama_model,
        "prompt": prompt,
        "stream": on_text is not None,
        "format": "json",
        "options": {"temperature": temperature},
    }

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    try:
        if on_text is None:
            return await _generate_once(url, payload, timeout_seconds)
        return await _generate_stream(url, payload, timeout_seconds, on_text)
    except httpx.HTTPError as exc:
        logger.error("Ollama request failed: {}", exc)
        raise OllamaError(f"Ollama request failed: {exc}") from exc


async def _generate_once(url: str, payload: dict, timeout_seconds: int) -> str:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
    content = response.json().get("response", "")
    if not content.strip():
        raise OllamaError("Ollama returned an empty response")
    return content


async def _generate_stream(
    url: str,
    payload: dict,
    timeout_seconds: int,
    on_text: TextProgress,
) -> str:
    parts: list[str] = []
    received = 0
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                added, done = consume_stream_line(parts, line)
                received += added
                if added:
                    await on_text(received)
                if done:
                    break
    content = "".join(parts)
    if not content.strip():
        raise OllamaError("Ollama returned an empty response")
    return content
