from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import ResumeStatus


class ExperienceDTO(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    location: str | None = None


class ProjectDTO(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class EducationDTO(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ParsedResumeResponse(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceDTO] = Field(default_factory=list)
    projects: list[ProjectDTO] = Field(default_factory=list)
    education: list[EducationDTO] = Field(default_factory=list)
    summary: str | None = None
    raw_text: str | None = None
    parser_version: str
    parsed_at: datetime


class ResumeResponse(BaseModel):
    id: str
    filename: str
    file_url: str | None = None
    status: ResumeStatus
    is_primary: bool
    parse_progress: int = 0
    parse_stage: str = "queued"
    created_at: datetime


class ResumeDetailResponse(BaseModel):
    id: str
    filename: str
    file_url: str | None = None
    status: ResumeStatus
    is_primary: bool
    parse_progress: int = 0
    parse_stage: str = "queued"
    parse_error: str | None = None
    parsed_resume: ParsedResumeResponse | None = None
    created_at: datetime


class ResumeListResponse(BaseModel):
    items: list[ResumeResponse]
    total: int
