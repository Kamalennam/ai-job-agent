import asyncio

from loguru import logger

from app.collectors.greenhouse.collector import GreenhouseCollector
from app.constants import SchedulerRunStatus
from app.db.client import close_db, connect_db
from app.events.jobs_collected import publish as publish_jobs_collected
from app.models.scheduler_log import SchedulerLog
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_repository import JobRepository
from app.repositories.scheduler_log_repository import SchedulerLogRepository
from app.workers.celery import celery


@celery.task(name="collect_jobs", queue="scraping")
def collect_jobs() -> None:
    asyncio.run(_collect_jobs_async())


async def _collect_jobs_async() -> None:
    await connect_db()
    try:
        await _collect_jobs()
    finally:
        await close_db()


async def _collect_jobs() -> None:
    log = SchedulerLog(job_name="collect_greenhouse", status=SchedulerRunStatus.STARTED)
    await SchedulerLogRepository.create(log)

    inserted = 0
    updated = 0
    failed = 0
    sources_used: list[str] = []

    try:
        collector = GreenhouseCollector()
        raw_jobs = await collector.collect()
        sources_used = [collector.source_name]

        for raw in raw_jobs:
            try:
                company_id = None
                if raw.company_slug:
                    careers_url = raw.source_url or f"https://boards.greenhouse.io/{raw.company_slug}"
                    company = await CompanyRepository.upsert_from_board(
                        slug=raw.company_slug,
                        name=raw.company,
                        careers_url=careers_url,
                    )
                    company_id = company.id
                    await CompanyRepository.mark_collected(company)

                _, is_new = await JobRepository.upsert_raw_job(raw, company_id)
                if is_new:
                    inserted += 1
                else:
                    updated += 1
            except Exception as exc:
                failed += 1
                logger.error("Failed to upsert job {}: {}", raw.source_id, exc)

        total = inserted + updated
        publish_jobs_collected(total, sources_used)

        await SchedulerLogRepository.complete(
            log,
            status=SchedulerRunStatus.SUCCESS,
            records_processed=total,
            records_failed=failed,
            metadata={
                "inserted": inserted,
                "updated": updated,
                "sources": sources_used,
            },
        )
        logger.info(
            "Greenhouse collection complete: {} new, {} updated, {} failed",
            inserted,
            updated,
            failed,
        )
    except Exception as exc:
        await SchedulerLogRepository.complete(
            log,
            status=SchedulerRunStatus.FAILED,
            records_failed=failed,
            error=str(exc),
        )
        logger.exception("Greenhouse collection failed")
        raise
