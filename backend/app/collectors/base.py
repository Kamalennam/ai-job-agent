from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawJob:
    title: str
    company: str
    location: str | None
    description: str
    source: str
    source_id: str
    apply_url: str
    source_url: str | None = None
    department: str | None = None
    employment_type: str | None = None
    posted_at: datetime | None = None
    remote: bool | None = None
    company_slug: str | None = None
