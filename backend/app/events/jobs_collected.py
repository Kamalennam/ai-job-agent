"""
Event: jobs_collected

Published when job_scraper worker finishes collecting jobs.
Triggers job_matcher worker (Phase 9).
"""


def publish(count: int, sources: list[str]) -> None:
    if count <= 0:
        return
    from loguru import logger

    from app.events.broker import broker_reachable
    from app.workers.job_matcher import score_all

    if not broker_reachable():
        logger.warning("Skipping job scoring queue; broker is unreachable")
        return
    try:
        score_all.delay()
    except Exception as exc:
        logger.warning("Job scoring could not be queued: {}", exc)
