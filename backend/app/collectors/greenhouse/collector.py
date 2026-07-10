import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx
from loguru import logger

from app.collectors.base import RawJob
from app.utils.config_loader import load_job_sources_config

GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards"
REMOTE_KEYWORDS = ("remote", "work from home", "wfh", "distributed")


class GreenhouseCollector:
    source_name = "greenhouse"

    async def collect(self) -> list[RawJob]:
        config = load_job_sources_config()
        greenhouse_cfg = config.get("sources", {}).get("greenhouse", {})
        if not greenhouse_cfg.get("enabled", False):
            logger.info("Greenhouse collector is disabled in config")
            return []

        boards = greenhouse_cfg.get("boards", [])
        slugs = [_slug_from_board_url(board) for board in boards]
        slugs = [slug for slug in slugs if slug]

        jobs: list[RawJob] = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for slug in slugs:
                try:
                    board_jobs = await self._fetch_board_jobs(client, slug)
                    jobs.extend(board_jobs)
                    logger.info(
                        "Collected {} jobs from Greenhouse board '{}'",
                        len(board_jobs),
                        slug,
                    )
                except Exception as exc:
                    logger.error("Failed to collect Greenhouse board '{}': {}", slug, exc)
        return jobs

    async def _fetch_board_jobs(self, client: httpx.AsyncClient, slug: str) -> list[RawJob]:
        url = f"{GREENHOUSE_API}/{slug}/jobs"
        response = await client.get(url, params={"content": "true"})
        response.raise_for_status()
        payload = response.json()

        company_name = payload.get("name") or slug.replace("-", " ").title()
        raw_jobs = payload.get("jobs", [])
        results: list[RawJob] = []

        for item in raw_jobs:
            location = _extract_location(item.get("location"))
            description = _extract_description(item)
            absolute_url = item.get("absolute_url") or f"https://boards.greenhouse.io/{slug}/jobs/{item.get('id')}"
            posted_at = _parse_updated_at(item.get("updated_at") or item.get("created_at"))

            results.append(
                RawJob(
                    title=item.get("title", "Untitled"),
                    company=company_name,
                    location=location,
                    description=description,
                    source=self.source_name,
                    source_id=str(item.get("id")),
                    apply_url=absolute_url,
                    source_url=absolute_url,
                    department=_extract_department(item),
                    employment_type=_extract_metadata(item, "employment_type"),
                    posted_at=posted_at,
                    remote=_is_remote(location, description),
                    company_slug=slug,
                )
            )
        return results


def _slug_from_board_url(board: str) -> str | None:
    if not board:
        return None
    if "://" not in board:
        return board.strip().strip("/")
    path = urlparse(board).path.strip("/")
    parts = path.split("/")
    return parts[-1] if parts else None


def _extract_location(location: dict | str | None) -> str | None:
    if isinstance(location, dict):
        return location.get("name")
    if isinstance(location, str):
        return location
    return None


def _extract_description(item: dict) -> str:
    content = item.get("content") or ""
    if content:
        return _strip_html(content)
    metadata = item.get("metadata") or []
    parts = [entry.get("value", "") for entry in metadata if entry.get("value")]
    return "\n".join(parts).strip() or item.get("title", "")


def _extract_department(item: dict) -> str | None:
    departments = item.get("departments") or []
    if departments:
        return departments[0].get("name")
    return None


def _extract_metadata(item: dict, key: str) -> str | None:
    for entry in item.get("metadata") or []:
        if entry.get("name", "").lower() == key:
            return entry.get("value")
    return None


def _parse_updated_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).astimezone(UTC)
    except ValueError:
        return None


def _is_remote(location: str | None, description: str) -> bool:
    haystack = f"{location or ''} {description}".lower()
    return any(keyword in haystack for keyword in REMOTE_KEYWORDS)


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()
