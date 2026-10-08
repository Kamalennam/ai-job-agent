from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field

from app.constants import ResumeStatus


class Resume(Document):
    user_id: Indexed(PydanticObjectId)
    filename: str
    file_path: str
    file_url: str | None = None
    file_size: int
    mime_type: str
    status: ResumeStatus = ResumeStatus.PENDING
    is_primary: bool = False
    parse_progress: int = 0
    parse_stage: str = "queued"
    parse_error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "resumes"
        indexes = [
            [("user_id", 1)],
            [("user_id", 1), ("status", 1)],
            [("user_id", 1), ("is_primary", 1)],
        ]
