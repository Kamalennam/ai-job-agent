from beanie import PydanticObjectId

from app.constants import ResumeStatus
from app.models.resume import Resume
from app.repositories.job_repository import JobRepository
from app.repositories.parsed_resume_repository import ParsedResumeRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.dashboard import DashboardOverview, DashboardProfile, DashboardResponse
from app.services.jobs.match_service import JobMatchService

RECENT_MATCH_LIMIT = 5


class DashboardService:
    @staticmethod
    async def aggregate(user_id: PydanticObjectId) -> DashboardResponse:
        resumes = await ResumeRepository.list_by_user(user_id)
        parsed_count = sum(1 for resume in resumes if resume.status == ResumeStatus.PARSED)
        total_jobs = await JobRepository.count_active()
        focus = DashboardService._focus_resume(resumes)

        profile: DashboardProfile | None = None
        recent_matches = []
        total_matches = 0
        scoring = False

        if focus is not None:
            profile = await DashboardService._profile(focus)
            if focus.status == ResumeStatus.PARSED:
                matches = await JobMatchService.match_jobs(
                    user_id=user_id,
                    resume_id=str(focus.id),
                    page=1,
                    page_size=RECENT_MATCH_LIMIT,
                )
                recent_matches = matches.jobs
                total_matches = matches.total_matched_jobs
                scoring = matches.scoring

        return DashboardResponse(
            overview=DashboardOverview(
                total_resumes=len(resumes),
                parsed_resumes=parsed_count,
                total_jobs=total_jobs,
                total_matches=total_matches,
            ),
            profile=profile,
            recent_matches=recent_matches,
            scoring=scoring,
        )

    @staticmethod
    def _focus_resume(resumes: list[Resume]) -> Resume | None:
        if not resumes:
            return None
        primary = next((resume for resume in resumes if resume.is_primary), None)
        if primary and primary.status == ResumeStatus.PARSED:
            return primary
        parsed = next((resume for resume in resumes if resume.status == ResumeStatus.PARSED), None)
        if parsed:
            return parsed
        return resumes[0]

    @staticmethod
    async def _profile(resume: Resume) -> DashboardProfile:
        profile = DashboardProfile(
            resume_id=str(resume.id),
            filename=resume.filename,
            status=resume.status,
            is_primary=resume.is_primary,
        )
        if resume.status != ResumeStatus.PARSED:
            return profile

        parsed = await ParsedResumeRepository.get_by_resume_id(resume.id)
        if not parsed or str(parsed.user_id) != str(resume.user_id):
            return profile

        current = parsed.experience[0] if parsed.experience else None
        profile.name = parsed.name
        profile.email = parsed.email
        profile.phone = parsed.phone
        profile.summary = parsed.summary
        profile.skills = list(parsed.skills or [])
        if current:
            profile.current_title = current.title
            profile.current_company = current.company
        return profile
