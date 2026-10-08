import asyncio

from loguru import logger

from app.db.client import close_db, connect_db
from app.repositories.resume_repository import ResumeRepository
from app.workers.celery import celery


@celery.task(name="score_resume", queue="matching", ignore_result=True)
def score_resume(resume_id: str) -> None:
    asyncio.run(_score_resume_async(resume_id))


async def score_resume_now(resume_id: str) -> None:
    """Score using the caller's event loop and its existing database connection."""
    from app.services.jobs.match_service import JobMatchService

    await JobMatchService.rebuild(resume_id)


async def _score_resume_async(resume_id: str) -> None:
    await connect_db()
    try:
        await score_resume_now(resume_id)
    finally:
        await close_db()


@celery.task(name="score_all", queue="matching", ignore_result=True)
def score_all() -> None:
    asyncio.run(_score_all_async())


async def _score_all_async() -> None:
    await connect_db()
    try:
        resume_ids = await ResumeRepository.list_parsed_ids()
        logger.info("Scoring jobs for {} parsed resumes", len(resume_ids))
        for resume_id in resume_ids:
            await score_resume_now(str(resume_id))
    finally:
        await close_db()
