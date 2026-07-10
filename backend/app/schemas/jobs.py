from datetime import datetime

from pydantic import BaseModel, Field

from app.constants import JobSource


class JobSearchParams(BaseModel):
    query: str | None = None
    remote: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str | None
    source: JobSource
    remote: bool | None
    posted_at: datetime | None
    apply_url: str


class JobDetailResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str | None
    description: str
    department: str | None
    employment_type: str | None
    source: JobSource
    source_url: str | None
    apply_url: str
    remote: bool | None
    posted_at: datetime | None
    collected_at: datetime


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int


class CollectJobsRequest(BaseModel):
    sources: list[str] | None = None


class JobSourceDTO(BaseModel):
    name: str
    enabled: bool
    last_collected_at: datetime | None
    job_count: int


class JobSourcesResponse(BaseModel):
    sources: list[JobSourceDTO]
