from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class Profile(Document):
    user_id: Indexed(PydanticObjectId, unique=True)
    full_name: str
    headline: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "profiles"
