from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field

from app.constants import SchedulerRunStatus


class SchedulerLog(Document):
    job_name: Indexed(str)
    status: SchedulerRunStatus
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_ms: int | None = None
    records_processed: int = 0
    records_failed: int = 0
    error: str | None = None
    metadata: dict | None = None

    class Settings:
        name = "scheduler_logs"
        indexes = [
            [("job_name", 1), ("started_at", -1)],
            [("status", 1), ("started_at", -1)],
        ]
