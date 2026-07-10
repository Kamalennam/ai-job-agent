from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class Session(Document):
    user_id: Indexed(PydanticObjectId)
    refresh_token_hash: str
    user_agent: str | None = None
    ip_address: str | None = None
    expires_at: datetime
    revoked: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "sessions"
        indexes = [
            [("user_id", 1)],
            [("expires_at", 1)],
            [("refresh_token_hash", 1)],
        ]
