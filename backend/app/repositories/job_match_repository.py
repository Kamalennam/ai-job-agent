import re
from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.job_match import JobMatch
from beanie import PydanticObjectId
from beanie.operators import Or, RegEx


@dataclass
class JobMatchWrite:
    job_id: str
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    matched_role: bool
    experience_match: bool
    project_matches: list[str]
    match_reasons: list[str]
    title: str
    company: str
    location: str | None
    url: str
    remote: bool | None
    posted_at: datetime | None


def _same_moment(left: datetime | None, right: datetime | None) -> bool:
    if left is None or right is None:
        return left is right
    return int(left.timestamp() * 1000) == int(right.timestamp() * 1000)


class JobMatchRepository:
    @staticmethod
    async def get_fresh(
        *,
        user_id: PydanticObjectId,
        resume_id: PydanticObjectId,
        profile_updated_at: datetime,
        active_job_count: int,
        latest_job_collected_at: datetime | None,
        min_score: int,
        scorer_version: str,
    ) -> list[JobMatch] | None:
        rows = await JobMatch.find(
            JobMatch.user_id == user_id,
            JobMatch.resume_id == resume_id,
            JobMatch.scorer_version == scorer_version,
            JobMatch.min_score == min_score,
        ).to_list()
        if not rows:
            return None
        sample = rows[0]
        if sample.active_job_count != active_job_count:
            return None
        if not _same_moment(sample.profile_updated_at, profile_updated_at):
            return None
        if not _same_moment(sample.latest_job_collected_at, latest_job_collected_at):
            return None
        return rows

    @staticmethod
    async def freshness_sample(
        *,
        user_id: PydanticObjectId,
        resume_id: PydanticObjectId,
        min_score: int,
        scorer_version: str,
    ) -> JobMatch | None:
        return await JobMatch.find(
            JobMatch.user_id == user_id,
            JobMatch.resume_id == resume_id,
            JobMatch.scorer_version == scorer_version,
            JobMatch.min_score == min_score,
        ).first_or_none()

    @staticmethod
    def is_current(
        sample: JobMatch,
        *,
        profile_updated_at: datetime,
        active_job_count: int,
        latest_job_collected_at: datetime | None,
    ) -> bool:
        if sample.active_job_count != active_job_count:
            return False
        if not _same_moment(sample.profile_updated_at, profile_updated_at):
            return False
        return _same_moment(sample.latest_job_collected_at, latest_job_collected_at)

    @staticmethod
    async def page(
        *,
        user_id: PydanticObjectId,
        resume_id: PydanticObjectId,
        min_score: int,
        scorer_version: str,
        page: int,
        page_size: int,
        query: str | None = None,
        remote: bool | None = None,
    ) -> tuple[list[JobMatch], int]:
        clauses: list[object] = [
            JobMatch.user_id == user_id,
            JobMatch.resume_id == resume_id,
            JobMatch.scorer_version == scorer_version,
            JobMatch.min_score == min_score,
        ]
        if remote is not None:
            clauses.append(JobMatch.remote == remote)
        if query and query.strip():
            pattern = re.escape(query.strip())
            clauses.append(
                Or(
                    RegEx(JobMatch.title, pattern, "i"),
                    RegEx(JobMatch.company, pattern, "i"),
                    RegEx(JobMatch.location, pattern, "i"),
                )
            )
        total = await JobMatch.find(*clauses).count()
        skip = max(page - 1, 0) * page_size
        rows = (
            await JobMatch.find(*clauses)
            .sort(-JobMatch.match_score, +JobMatch.title, +JobMatch.job_id)
            .skip(skip)
            .limit(page_size)
            .to_list()
        )
        return rows, total

    @staticmethod
    async def replace_for_resume(
        *,
        user_id: PydanticObjectId,
        resume_id: PydanticObjectId,
        matches: list[JobMatchWrite],
        profile_updated_at: datetime,
        active_job_count: int,
        latest_job_collected_at: datetime | None,
        min_score: int,
        scorer_version: str,
    ) -> None:
        await JobMatch.find(
            JobMatch.user_id == user_id,
            JobMatch.resume_id == resume_id,
        ).delete()
        if not matches:
            return
        now = datetime.now(UTC)
        docs = [
            JobMatch(
                user_id=user_id,
                resume_id=resume_id,
                job_id=PydanticObjectId(item.job_id),
                match_score=item.match_score,
                matched_skills=item.matched_skills,
                missing_skills=item.missing_skills,
                matched_role=item.matched_role,
                experience_match=item.experience_match,
                project_matches=item.project_matches,
                match_reasons=item.match_reasons,
                title=item.title,
                company=item.company,
                location=item.location,
                url=item.url,
                remote=item.remote,
                posted_at=item.posted_at,
                profile_updated_at=profile_updated_at,
                active_job_count=active_job_count,
                latest_job_collected_at=latest_job_collected_at,
                min_score=min_score,
                scorer_version=scorer_version,
                created_at=now,
                updated_at=now,
            )
            for item in matches
        ]
        await JobMatch.insert_many(docs)

    @staticmethod
    async def delete_for_resume(resume_id: PydanticObjectId) -> None:
        await JobMatch.find(JobMatch.resume_id == resume_id).delete()
