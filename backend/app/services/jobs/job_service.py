from app.events.job_collection_requested import publish as publish_job_collection_requested
from app.models.job import Job
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_repository import JobRepository
from app.schemas.auth import MessageResponse
from app.schemas.jobs import (
    CollectJobsRequest,
    JobDetailResponse,
    JobListResponse,
    JobResponse,
    JobSearchParams,
    JobSourceDTO,
    JobSourcesResponse,
)


class JobService:
    @staticmethod
    async def search_jobs(params: JobSearchParams) -> JobListResponse:
        jobs, total = await JobRepository.search(
            query=params.query,
            remote=params.remote,
            page=params.page,
            page_size=params.page_size,
        )
        return JobListResponse(
            items=[JobService._to_response(job) for job in jobs],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    @staticmethod
    async def get_job(job_id: str) -> JobDetailResponse:
        job = await JobRepository.get_by_id(job_id)
        if not job or not job.is_active:
            from app.core.exceptions import AppException

            raise AppException(404, "NOT_FOUND", "Job not found")
        return JobService._to_detail_response(job)

    @staticmethod
    async def trigger_collection(_request: CollectJobsRequest | None = None) -> MessageResponse:
        publish_job_collection_requested()
        return MessageResponse(message="Job collection started")

    @staticmethod
    async def list_sources() -> JobSourcesResponse:
        companies = await CompanyRepository.list_enabled_greenhouse()
        total_jobs = await JobRepository.count_active()
        per_company = max(total_jobs // max(len(companies), 1), 0) if companies else total_jobs

        sources = [
            JobSourceDTO(
                name=company.slug,
                enabled=company.enabled,
                last_collected_at=company.last_collected_at,
                job_count=per_company,
            )
            for company in companies
        ]

        if not sources and total_jobs:
            sources = [
                JobSourceDTO(
                    name="greenhouse",
                    enabled=True,
                    last_collected_at=None,
                    job_count=total_jobs,
                )
            ]

        return JobSourcesResponse(sources=sources)

    @staticmethod
    def _to_response(job: Job) -> JobResponse:
        return JobResponse(
            id=str(job.id),
            title=job.title,
            company=job.company,
            location=job.location,
            source=job.source,
            remote=job.remote,
            posted_at=job.posted_at,
            apply_url=job.apply_url,
        )

    @staticmethod
    def _to_detail_response(job: Job) -> JobDetailResponse:
        return JobDetailResponse(
            id=str(job.id),
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            department=job.department,
            employment_type=job.employment_type,
            source=job.source,
            source_url=job.source_url,
            apply_url=job.apply_url,
            remote=job.remote,
            posted_at=job.posted_at,
            collected_at=job.collected_at,
        )
