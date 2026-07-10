import httpx
import redis.asyncio as redis
from fastapi import APIRouter

from app.config import get_settings
from app.db.client import get_database
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok", checks={"api": "ok"})


@router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    settings = get_settings()
    checks: dict[str, str] = {}

    try:
        db = get_database()
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as exc:
        checks["mongodb"] = f"error: {exc}"

    try:
        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
        checks["ollama"] = "ok"
    except Exception as exc:
        checks["ollama"] = f"error: {exc}"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return HealthResponse(status=status, checks=checks)
