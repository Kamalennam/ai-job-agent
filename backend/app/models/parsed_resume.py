from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class Experience(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    location: str | None = None


class Project(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class Education(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ParsedResume(Document):
    resume_id: Indexed(PydanticObjectId, unique=True)
    user_id: Indexed(PydanticObjectId)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    summary: str | None = None
    raw_text: str | None = None
    embedding: list[float] | None = None
    embedding_model: str | None = None
    parser_version: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "parsed_resumes"
        indexes = [
            [("resume_id", 1)],
            [("user_id", 1)],
        ]
