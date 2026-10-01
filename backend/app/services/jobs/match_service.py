from beanie import PydanticObjectId
from bson import ObjectId
from loguru import logger

from app.config import get_settings
from app.constants import ResumeStatus
from app.core.exceptions import AppException
from app.models.job import Job
from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume
from app.repositories.job_match_repository import JobMatchRepository, JobMatchWrite
from app.repositories.job_repository import JobRepository
from app.repositories.parsed_resume_repository import ParsedResumeRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.jobs import JobMatchListResponse, JobMatchResponse
from app.services.jobs.match_engine import (
    SCORER_VERSION,
    EducationInput,
    ExperienceInput,
    JobInput,
    MatchWeights,
    ParsedResumeInput,
    ProjectInput,
    ScoredMatch,
    build_candidate_profile,
    rank_jobs,
)


class JobMatchService:
    @staticmethod
    async def match_jobs(
        *,
        user_id: PydanticObjectId,
        resume_id: str | None,
        page: int,
        page_size: int,
        query: str | None = None,
        remote: bool | None = None,
    ) -> JobMatchListResponse:
        settings = get_settings()
        min_score = settings.min_job_match_score
        weights = MatchWeights(
            skill=settings.match_weight_skill,
            role=settings.match_weight_role,
            experience=settings.match_weight_experience,
            project=settings.match_weight_project,
            other=settings.match_weight_other,
        )
        resume = await JobMatchService._resolve_resume(user_id, resume_id)
        parsed = await JobMatchService._require_parsed_resume(user_id, resume)
        active_count, latest_collected_at = await JobRepository.matching_watermark()

        cached = await JobMatchRepository.get_fresh(
            user_id=user_id,
            resume_id=resume.id,
            profile_updated_at=parsed.updated_at,
            active_job_count=active_count,
            latest_job_collected_at=latest_collected_at,
            min_score=min_score,
            scorer_version=SCORER_VERSION,
        )
        if cached is None:
            jobs = await JobRepository.list_active()
            profile = build_candidate_profile(JobMatchService._to_profile_input(parsed))
            matched, analyzed = rank_jobs(
                profile,
                [JobMatchService._to_job_input(job) for job in jobs],
                min_score=min_score,
                weights=weights,
            )
            await JobMatchRepository.replace_for_resume(
                user_id=user_id,
                resume_id=resume.id,
                matches=[JobMatchService._to_write(item) for item in matched],
                profile_updated_at=parsed.updated_at,
                active_job_count=analyzed,
                latest_job_collected_at=latest_collected_at,
                min_score=min_score,
                scorer_version=SCORER_VERSION,
            )
            pool = matched
            total_analyzed = analyzed
        else:
            pool = [JobMatchService._from_cached(row) for row in cached]
            total_analyzed = active_count

        filtered = [
            item
            for item in pool
            if JobMatchService._passes_filters(item, query=query, remote=remote)
        ]
        filtered.sort(key=lambda item: (-item.match_score, item.title.lower(), item.job_id))
        start = (page - 1) * page_size
        page_items = filtered[start : start + page_size]

        logger.info(
            "Matched jobs for resume {}: analyzed={} matched={} page={}",
            resume.id,
            total_analyzed,
            len(filtered),
            page,
        )
        return JobMatchListResponse(
            resume_id=str(resume.id),
            total_jobs_analyzed=total_analyzed,
            total_matched_jobs=len(filtered),
            page=page,
            page_size=page_size,
            jobs=[JobMatchService._to_response(item) for item in page_items],
        )

    @staticmethod
    async def _resolve_resume(user_id: PydanticObjectId, resume_id: str | None) -> Resume:
        if resume_id:
            if not ObjectId.is_valid(resume_id):
                raise AppException(404, "NOT_FOUND", "Resume not found")
            resume = await ResumeRepository.get_by_id(resume_id)
            if not resume or str(resume.user_id) != str(user_id):
                raise AppException(404, "NOT_FOUND", "Resume not found")
            return resume

        resume = await ResumeRepository.get_primary_for_user(user_id)
        if not resume:
            raise AppException(
                400,
                "RESUME_REQUIRED",
                "Select or upload a resume before matching jobs.",
            )
        return resume

    @staticmethod
    async def _require_parsed_resume(
        user_id: PydanticObjectId,
        resume: Resume,
    ) -> ParsedResume:
        if resume.status != ResumeStatus.PARSED:
            raise AppException(
                409,
                "RESUME_NOT_PARSED",
                "Resume parsing is not complete. Wait until parsing finishes before matching jobs.",
            )
        parsed = await ParsedResumeRepository.get_by_resume_id(resume.id)
        if not parsed or str(parsed.user_id) != str(user_id):
            raise AppException(
                409,
                "RESUME_NOT_PARSED",
                "This resume has no parsed profile yet.",
            )
        return parsed

    @staticmethod
    def _passes_filters(item: ScoredMatch, *, query: str | None, remote: bool | None) -> bool:
        if remote is not None and item.remote is not remote:
            return False
        if query:
            haystack = f"{item.title} {item.company} {item.location or ''}".lower()
            if query.strip().lower() not in haystack:
                return False
        return True

    @staticmethod
    def _to_profile_input(parsed: ParsedResume) -> ParsedResumeInput:
        return ParsedResumeInput(
            skills=list(parsed.skills or []),
            experience=[
                ExperienceInput(
                    title=item.title,
                    company=item.company,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    description=item.description,
                )
                for item in parsed.experience or []
            ],
            projects=[
                ProjectInput(
                    name=item.name,
                    technologies=list(item.technologies or []),
                    description=item.description,
                )
                for item in parsed.projects or []
            ],
            education=[
                EducationInput(
                    institution=item.institution,
                    degree=item.degree,
                    field=item.field,
                )
                for item in parsed.education or []
            ],
            summary=parsed.summary,
            raw_text=parsed.raw_text,
        )

    @staticmethod
    def _to_job_input(job: Job) -> JobInput:
        return JobInput(
            job_id=str(job.id),
            title=job.title,
            description=job.description or "",
            url=job.apply_url,
            company=job.company,
            location=job.location,
            department=job.department,
            employment_type=job.employment_type,
            requirements=job.requirements,
            remote=job.remote,
            posted_at=job.posted_at,
        )

    @staticmethod
    def _to_write(item: ScoredMatch) -> JobMatchWrite:
        return JobMatchWrite(
            job_id=item.job_id,
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
        )

    @staticmethod
    def _from_cached(row: object) -> ScoredMatch:
        return ScoredMatch(
            job_id=str(row.job_id),
            title=row.title,
            company=row.company,
            location=row.location,
            remote=row.remote,
            posted_at=row.posted_at,
            url=row.url,
            match_score=row.match_score,
            matched_skills=list(row.matched_skills),
            missing_skills=list(row.missing_skills),
            matched_role=row.matched_role,
            experience_match=row.experience_match,
            project_matches=list(row.project_matches),
            match_reasons=list(row.match_reasons),
            skill_score=0,
            role_score=0,
            experience_score=0,
            project_score=0,
            other_score=0,
        )

    @staticmethod
    def _to_response(item: ScoredMatch) -> JobMatchResponse:
        return JobMatchResponse(
            job_id=item.job_id,
            title=item.title,
            company=item.company,
            location=item.location,
            remote=item.remote,
            posted_at=item.posted_at,
            match_score=item.match_score,
            matched_skills=item.matched_skills,
            missing_skills=item.missing_skills,
            matched_role=item.matched_role,
            experience_match=item.experience_match,
            project_matches=item.project_matches,
            match_reasons=item.match_reasons,
            url=item.url,
        )
