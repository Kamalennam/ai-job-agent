from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.jobs import (
    CollectJobsRequest,
    JobDetailResponse,
    JobListResponse,
    JobSearchParams,
    JobSourcesResponse,
)
from app.services.jobs.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    query: str | None = Query(default=None),
    remote: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _current_user: User = Depends(get_current_user),
) -> JobListResponse:
    params = JobSearchParams(query=query, remote=remote, page=page, page_size=page_size)
    return await JobService.search_jobs(params)


@router.get("/sources", response_model=JobSourcesResponse)
async def list_sources(_current_user: User = Depends(get_current_user)) -> JobSourcesResponse:
    return await JobService.list_sources()


@router.post("/collect", response_model=MessageResponse)
async def collect_jobs(
    request: CollectJobsRequest | None = None,
    _current_user: User = Depends(get_current_user),
) -> MessageResponse:
    return await JobService.trigger_collection(request)


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: str,
    _current_user: User = Depends(get_current_user),
) -> JobDetailResponse:
    return await JobService.get_job(job_id)
