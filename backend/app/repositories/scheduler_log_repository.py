from datetime import UTC, datetime

from app.constants import SchedulerRunStatus
from app.models.scheduler_log import SchedulerLog


class SchedulerLogRepository:
    @staticmethod
    async def create(log: SchedulerLog) -> SchedulerLog:
        return await log.insert()

    @staticmethod
    async def complete(
        log: SchedulerLog,
        *,
        status: SchedulerRunStatus,
        records_processed: int = 0,
        records_failed: int = 0,
        error: str | None = None,
        metadata: dict | None = None,
    ) -> SchedulerLog:
        completed_at = datetime.now(UTC)
        log.status = status
        log.completed_at = completed_at
        log.duration_ms = int((completed_at - log.started_at).total_seconds() * 1000)
        log.records_processed = records_processed
        log.records_failed = records_failed
        log.error = error
        log.metadata = metadata
        await log.save()
        return log
