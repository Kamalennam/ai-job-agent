from loguru import logger

from app.workers.celery import celery


@celery.task(name="score_all", queue="matching")
def score_all() -> None:
    logger.info(
        "Scheduled batch matching is not implemented yet. "
        "Interactive matching is GET /api/v1/jobs/matches"
    )
