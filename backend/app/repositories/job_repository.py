from datetime import UTC, datetime

from app.collectors.base import RawJob
from app.constants import JobSource
from app.models.job import Job
from beanie import PydanticObjectId


class JobRepository:
    @staticmethod
    async def get_by_id(job_id: str | PydanticObjectId) -> Job | None:
        return await Job.get(PydanticObjectId(str(job_id)))

    @staticmethod
    async def upsert_raw_job(raw: RawJob, company_id: PydanticObjectId | None) -> tuple[Job, bool]:
        source = JobSource(raw.source)
        existing = await Job.find_one(Job.source == source, Job.source_id == raw.source_id)

        if existing:
            existing.title = raw.title
            existing.company = raw.company
            existing.company_id = company_id
            existing.location = raw.location
            existing.description = raw.description
            existing.source_url = raw.source_url
            existing.apply_url = raw.apply_url
            existing.department = raw.department
            existing.employment_type = raw.employment_type
            existing.remote = raw.remote
            existing.posted_at = raw.posted_at
            existing.collected_at = datetime.now(UTC)
            existing.is_active = True
            await existing.save()
            return existing, False

        job = Job(
            title=raw.title,
            company=raw.company,
            company_id=company_id,
            location=raw.location,
            description=raw.description,
            source=source,
            source_id=raw.source_id,
            source_url=raw.source_url,
            apply_url=raw.apply_url,
            department=raw.department,
            employment_type=raw.employment_type,
            remote=raw.remote,
            posted_at=raw.posted_at,
            is_active=True,
        )
        await job.insert()
        return job, True

    @staticmethod
    async def search(
        *,
        query: str | None = None,
        remote: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Job], int]:
        filters: dict = {"is_active": True}
        if remote is not None:
            filters["remote"] = remote

        cursor = Job.find(filters)
        if query:
            regex = {"$regex": query, "$options": "i"}
            cursor = Job.find(
                {
                    **filters,
                    "$or": [
                        {"title": regex},
                        {"company": regex},
                        {"location": regex},
                        {"description": regex},
                    ],
                }
            )

        total = await cursor.count()
        skip = max(page - 1, 0) * page_size
        jobs = await cursor.sort(-Job.collected_at).skip(skip).limit(page_size).to_list()
        return jobs, total

    @staticmethod
    async def count_active() -> int:
        return await Job.find(Job.is_active == True).count()  # noqa: E712

    @staticmethod
    async def list_active() -> list[Job]:
        return await Job.find(Job.is_active == True).to_list()  # noqa: E712

    @staticmethod
    async def matching_watermark() -> tuple[int, datetime | None]:
        count = await Job.find(Job.is_active == True).count()  # noqa: E712
        latest = (
            await Job.find(Job.is_active == True)  # noqa: E712
            .sort(-Job.collected_at)
            .limit(1)
            .to_list()
        )
        latest_at = latest[0].collected_at if latest else None
        return count, latest_at
