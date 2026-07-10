from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field


class Company(Document):
    name: Indexed(str, unique=True)
    slug: Indexed(str, unique=True)
    website: str | None = None
    ats_type: str = "greenhouse"
    careers_url: str | None = None
    enabled: bool = True
    last_collected_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "companies"
        indexes = [
            [("enabled", 1), ("ats_type", 1)],
        ]
