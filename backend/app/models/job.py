from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field

from app.constants import JobSource


class Job(Document):
    title: str
    company: Indexed(str)
    company_id: PydanticObjectId | None = None
    location: str | None = None
    description: str
    requirements: str | None = None
    source: JobSource
    source_id: str
    source_url: str | None = None
    apply_url: str
    department: str | None = None
    employment_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    remote: bool | None = None
    posted_at: datetime | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    embedding: list[float] | None = None
    embedding_model: str | None = None

    class Settings:
        name = "jobs"
        indexes = [
            [("source", 1), ("source_id", 1)],
            [("company_id", 1)],
            [("posted_at", -1)],
            [("remote", 1), ("is_active", 1)],
        ]
