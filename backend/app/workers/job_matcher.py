from loguru import logger

from app.workers.celery import celery


@celery.task(name="score_all", queue="matching")
def score_all() -> None:
    logger.info("Job matching is not implemented yet (Phase 9)")
