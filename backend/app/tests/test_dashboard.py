from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bson import ObjectId

from app.constants import ResumeStatus
from app.schemas.jobs import JobMatchListResponse, JobMatchResponse
from app.services.dashboard.dashboard_service import DashboardService


def _resume(*, status: ResumeStatus, is_primary: bool, filename: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=ObjectId(),
        filename=filename,
        status=status,
        is_primary=is_primary,
        user_id=ObjectId(),
    )


def _match_page(resume_id: str, *, scoring: bool = False) -> JobMatchListResponse:
    return JobMatchListResponse(
        resume_id=resume_id,
        total_jobs_analyzed=10,
        total_matched_jobs=1,
        page=1,
        page_size=5,
        scoring=scoring,
        jobs=[
            JobMatchResponse(
                job_id=str(ObjectId()),
                title="Backend Engineer",
                company="Acme",
                match_score=82,
                matched_skills=["Python"],
                missing_skills=[],
                matched_role=True,
                experience_match=True,
                project_matches=[],
                match_reasons=["Skills overlap"],
                url="https://example.com/jobs/1",
                posted_at=datetime(2026, 10, 1, tzinfo=UTC),
            )
        ],
    )


async def test_aggregate_uses_primary_parsed_resume() -> None:
    user_id = ObjectId()
    primary = _resume(status=ResumeStatus.PARSED, is_primary=True, filename="primary.pdf")
    older = _resume(status=ResumeStatus.PARSED, is_primary=False, filename="older.pdf")
    parsed = SimpleNamespace(
        user_id=primary.user_id,
        name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        summary="Builds APIs.",
        skills=["Python", "FastAPI"],
        experience=[SimpleNamespace(title="Engineer", company="Acme")],
    )
    matches = _match_page(str(primary.id))

    with (
        patch(
            "app.services.dashboard.dashboard_service.ResumeRepository.list_by_user",
            new=AsyncMock(return_value=[primary, older]),
        ),
        patch(
            "app.services.dashboard.dashboard_service.JobRepository.count_active",
            new=AsyncMock(return_value=12),
        ),
        patch(
            "app.services.dashboard.dashboard_service.ParsedResumeRepository.get_by_resume_id",
            new=AsyncMock(return_value=parsed),
        ) as get_parsed,
        patch(
            "app.services.dashboard.dashboard_service.JobMatchService.match_jobs",
            new=AsyncMock(return_value=matches),
        ) as match_jobs,
    ):
        result = await DashboardService.aggregate(user_id)

    assert result.overview.total_resumes == 2
    assert result.overview.parsed_resumes == 2
    assert result.overview.total_jobs == 12
    assert result.overview.total_matches == 1
    assert result.profile is not None
    assert result.profile.resume_id == str(primary.id)
    assert result.profile.name == "Ada Lovelace"
    assert result.profile.current_title == "Engineer"
    assert result.profile.current_company == "Acme"
    assert result.scoring is False
    assert len(result.recent_matches) == 1
    get_parsed.assert_awaited_once_with(primary.id)
    match_jobs.assert_awaited_once()
    assert match_jobs.await_args.kwargs["resume_id"] == str(primary.id)


async def test_aggregate_skips_matching_when_resume_is_still_parsing() -> None:
    user_id = ObjectId()
    pending = _resume(status=ResumeStatus.PARSING, is_primary=True, filename="new.pdf")

    with (
        patch(
            "app.services.dashboard.dashboard_service.ResumeRepository.list_by_user",
            new=AsyncMock(return_value=[pending]),
        ),
        patch(
            "app.services.dashboard.dashboard_service.JobRepository.count_active",
            new=AsyncMock(return_value=4),
        ),
        patch(
            "app.services.dashboard.dashboard_service.JobMatchService.match_jobs",
            new=AsyncMock(),
        ) as match_jobs,
    ):
        result = await DashboardService.aggregate(user_id)

    assert result.overview.total_resumes == 1
    assert result.overview.parsed_resumes == 0
    assert result.overview.total_matches == 0
    assert result.profile is not None
    assert result.profile.status == ResumeStatus.PARSING
    assert result.profile.name is None
    assert result.recent_matches == []
    assert result.scoring is False
    match_jobs.assert_not_awaited()


async def test_aggregate_is_empty_without_resumes() -> None:
    user_id = ObjectId()

    with (
        patch(
            "app.services.dashboard.dashboard_service.ResumeRepository.list_by_user",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "app.services.dashboard.dashboard_service.JobRepository.count_active",
            new=AsyncMock(return_value=0),
        ),
    ):
        result = await DashboardService.aggregate(user_id)

    assert result.profile is None
    assert result.overview.total_resumes == 0
    assert result.overview.total_jobs == 0
    assert result.recent_matches == []
