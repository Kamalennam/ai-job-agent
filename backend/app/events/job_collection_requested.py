"""
Event: job_collection_requested

Published when a user manually triggers job collection from the API.
Triggers job_scraper worker.
"""

from loguru import logger

from app.core.exceptions import AppException
from app.events.broker import broker_reachable
from app.workers.job_scraper import collect_jobs


def publish() -> None:
    if not broker_reachable():
        logger.warning("Job collection broker is unreachable")
        raise AppException(
            503,
            "SERVICE_UNAVAILABLE",
            "Job collection is unavailable right now. Try again in a few minutes.",
        )
    try:
        collect_jobs.delay()
    except Exception as exc:
        logger.warning("Job collection could not be queued: {}", exc)
        raise AppException(
            503,
            "SERVICE_UNAVAILABLE",
            "Job collection is unavailable right now. Try again in a few minutes.",
        ) from exc
