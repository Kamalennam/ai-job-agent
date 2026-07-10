from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class UserSettings(Document):
    user_id: Indexed(PydanticObjectId, unique=True)
    match_threshold: float = 70.0
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_titles: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    remote_only: bool = False
    enabled_sources: list[str] = Field(default_factory=lambda: ["greenhouse"])
    ai_model: str = "llama3.2"
    embedding_model: str = "nomic-embed-text"
    auto_match_enabled: bool = True
    email_notifications: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "settings"
