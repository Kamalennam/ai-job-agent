from pydantic import BaseModel, Field

from app.constants import ResumeStatus
from app.schemas.jobs import JobMatchResponse


class DashboardOverview(BaseModel):
    total_resumes: int
    parsed_resumes: int
    total_jobs: int
    total_matches: int


class DashboardProfile(BaseModel):
    resume_id: str
    filename: str
    status: ResumeStatus
    is_primary: bool
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    current_title: str | None = None
    current_company: str | None = None


class DashboardResponse(BaseModel):
    overview: DashboardOverview
    profile: DashboardProfile | None = None
    recent_matches: list[JobMatchResponse] = Field(default_factory=list)
    scoring: bool = False
