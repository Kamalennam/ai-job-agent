from pydantic import BaseModel, Field


class ExperienceExtract(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    location: str | None = None


class ProjectExtract(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class EducationExtract(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ResumeExtractionResult(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceExtract] = Field(default_factory=list)
    projects: list[ProjectExtract] = Field(default_factory=list)
    education: list[EducationExtract] = Field(default_factory=list)
    summary: str | None = None
