from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId

from app.constants import ResumeStatus
from app.core.exceptions import AppException
from app.services.jobs.match_engine import (
    EducationInput,
    ExperienceInput,
    JobInput,
    ParsedResumeInput,
    ProjectInput,
    build_candidate_profile,
    rank_jobs,
    score_job,
)
from app.services.jobs.match_service import JobMatchService
from app.services.jobs.skill_normalizer import find_skills, normalize_skill

BACKEND_JD = (
    "Backend Engineer We are hiring a Backend Engineer to build APIs. "
    "Responsibilities Design services and use MongoDB for persistence. "
    "Requirements 4+ years of experience building production systems. "
    "Python FastAPI AWS Docker "
    "Preferred Kubernetes PostgreSQL"
)
PARTIAL_JD = (
    "Backend Engineer "
    "Requirements 4+ years of experience building production systems. "
    "Python FastAPI AWS Docker Kubernetes PostgreSQL"
)
AI_JD = (
    "AI Engineer Build retrieval systems. "
    "Requirements 3+ years of experience. "
    "Python PyTorch LangChain RAG LLM "
    "Preferred Kubernetes"
)
IOS_JD = (
    "iOS Engineer Build mobile apps. "
    "Requirements 4+ years of experience. "
    "Swift UIKit Objective-C"
)
SENIOR_JD = (
    "Senior Backend Engineer "
    "Requirements 8+ years of experience. "
    "Python FastAPI AWS Docker "
    "Preferred Kubernetes PostgreSQL "
    "Responsibilities Design services and use MongoDB for persistence."
)


def _experience(
    title: str,
    *,
    start: str = "2020-01",
    end: str = "2026-01",
    description: str = "",
) -> ExperienceInput:
    return ExperienceInput(
        title=title,
        company="Acme",
        start_date=start,
        end_date=end,
        description=description,
    )


def _profile(
    *,
    skills: list[str],
    title: str,
    summary: str,
    projects: list[str] | None = None,
    start: str = "2020-01",
    end: str = "2026-01",
    description: str = "",
    raw_text: str = "",
) -> ParsedResumeInput:
    return ParsedResumeInput(
        skills=skills,
        experience=[_experience(title, start=start, end=end, description=description)],
        projects=[
            ProjectInput(name="Platform", technologies=projects or [], description=""),
        ],
        education=[
            EducationInput(institution="State University", degree="BS", field="Computer Science"),
        ],
        summary=summary,
        raw_text=raw_text,
    )


def _job(title: str, description: str, job_id: str = "job-1", company: str = "Acme") -> JobInput:
    return JobInput(
        job_id=job_id,
        title=title,
        description=description,
        url=f"https://boards.greenhouse.io/acme/jobs/{job_id}",
        company=company,
        location="Remote",
        remote=True,
    )


def _backend_profile(**overrides: object) -> ParsedResumeInput:
    payload = {
        "skills": ["Python", "FastAPI", "AWS", "Docker", "PostgreSQL"],
        "title": "Backend Engineer",
        "summary": "Backend engineer building Python APIs",
        "projects": ["FastAPI", "MongoDB", "AWS"],
    }
    payload.update(overrides)
    return _profile(**payload)  # type: ignore[arg-type]


def _ai_profile() -> ParsedResumeInput:
    return _profile(
        skills=["Python", "PyTorch", "LangChain", "RAG", "LLM"],
        title="AI Engineer",
        summary="AI engineer building RAG systems",
        projects=["LangChain", "PyTorch"],
    )


def _ios_profile() -> ParsedResumeInput:
    return _profile(
        skills=["Swift", "UIKit"],
        title="iOS Engineer",
        summary="iOS engineer building Swift apps",
        projects=["UIKit"],
    )


def test_skill_aliases_avoid_false_positives() -> None:
    assert normalize_skill("React.js") == "react"
    assert normalize_skill("fast api") == "fastapi"
    assert normalize_skill("AWS EC2") == "aws"
    assert normalize_skill("postgres") == "postgresql"
    assert find_skills("JavaScript developer") == ["javascript"]
    assert find_skills("Java and JavaScript") == ["java", "javascript"]

    react_profile = build_candidate_profile(
        _profile(skills=["React.js"], title="Frontend Engineer", summary="Frontend engineer")
    )
    react_job = score_job(
        react_profile,
        _job(
            "Frontend Engineer",
            "Requirements 3+ years of experience. React AWS",
        ),
    )
    assert any(normalize_skill(skill) == "react" for skill in react_job.matched_skills)

    java_profile = build_candidate_profile(
        _profile(skills=["Java"], title="Backend Engineer", summary="Backend engineer")
    )
    javascript_job = score_job(
        java_profile,
        _job("Frontend Engineer", "Requirements 3+ years of experience. JavaScript React"),
    )
    assert "Java" not in javascript_job.matched_skills
    assert "java" not in {normalize_skill(skill) for skill in javascript_job.matched_skills}


def test_profile_uses_experience_and_projects_not_only_skills() -> None:
    profile = build_candidate_profile(
        _profile(
            skills=["Python"],
            title="Backend Engineer",
            summary="Backend engineer",
            description="Built services with FastAPI",
            projects=["MongoDB"],
        )
    )
    result = score_job(profile, _job("Backend Engineer", BACKEND_JD, job_id="exp-1"))
    matched = {normalize_skill(skill) for skill in result.matched_skills}
    assert "fastapi" in matched
    assert "mongodb" in {normalize_skill(skill) for skill in result.project_matches}


def test_strong_skill_match() -> None:
    result = score_job(
        build_candidate_profile(_backend_profile()),
        _job("Backend Engineer", BACKEND_JD, job_id="strong"),
    )
    matched = {normalize_skill(skill) for skill in result.matched_skills}
    assert result.match_score >= 80
    assert {"python", "fastapi", "aws", "docker"} <= matched
    assert "Kubernetes" in result.missing_skills
    assert result.matched_role is True
    assert result.experience_match is True
    assert {normalize_skill(skill) for skill in result.project_matches} >= {
        "fastapi",
        "mongodb",
        "aws",
    }
    assert any(reason.startswith("Strong skill overlap") for reason in result.match_reasons)


def test_partial_skill_match() -> None:
    strong = score_job(
        build_candidate_profile(_backend_profile()),
        _job("Backend Engineer", PARTIAL_JD, job_id="full"),
    )
    partial = score_job(
        build_candidate_profile(
            _profile(
                skills=["Python", "Docker"],
                title="Backend Engineer",
                summary="Backend engineer",
                projects=[],
            )
        ),
        _job("Backend Engineer", PARTIAL_JD, job_id="partial"),
    )
    none = score_job(
        build_candidate_profile(_ios_profile()),
        _job("Backend Engineer", PARTIAL_JD, job_id="none"),
    )
    assert partial.matched_skills
    assert partial.missing_skills
    assert len(partial.matched_skills) < len(strong.matched_skills)
    assert none.match_score < partial.match_score < strong.match_score


def test_no_skill_match_is_filtered_by_threshold() -> None:
    profile = build_candidate_profile(_ios_profile())
    result = score_job(profile, _job("Backend Engineer", BACKEND_JD, job_id="ios-vs-be"))
    assert result.matched_skills == []
    assert result.match_score < 60
    matched, analyzed = rank_jobs(
        profile,
        [
            _job("Backend Engineer", BACKEND_JD, job_id="be"),
            _job("iOS Engineer", IOS_JD, job_id="ios"),
        ],
        min_score=60,
    )
    assert analyzed == 2
    assert [item.job_id for item in matched] == ["ios"]


def test_role_title_match() -> None:
    backend = score_job(
        build_candidate_profile(_backend_profile()),
        _job("Senior Backend Engineer", BACKEND_JD, job_id="role"),
    )
    mobile = score_job(
        build_candidate_profile(_ios_profile()),
        _job("Senior Backend Engineer", BACKEND_JD, job_id="role-miss"),
    )
    assert backend.matched_role is True
    assert any("role matches candidate experience" in reason for reason in backend.match_reasons)
    assert mobile.matched_role is False


def test_experience_mismatch() -> None:
    profile = build_candidate_profile(
        _backend_profile(start="2025-06", end="2026-01")
    )
    result = score_job(profile, _job("Senior Backend Engineer", SENIOR_JD, job_id="years"))
    assert result.experience_match is False
    assert any("below the 8+ year requirement" in reason for reason in result.match_reasons)
    assert result.matched_role is True


def test_same_job_scores_differ_for_two_resumes() -> None:
    backend_job = _job("Backend Engineer", BACKEND_JD, job_id="shared-backend")
    ai_job = _job("AI Engineer", AI_JD, job_id="shared-ai")
    backend_profile = build_candidate_profile(_backend_profile())
    ai_profile = build_candidate_profile(_ai_profile())

    backend_on_backend = score_job(backend_profile, backend_job)
    ai_on_backend = score_job(ai_profile, backend_job)
    backend_on_ai = score_job(backend_profile, ai_job)
    ai_on_ai = score_job(ai_profile, ai_job)

    assert backend_on_backend.match_score != ai_on_backend.match_score
    assert backend_on_backend.match_score > ai_on_backend.match_score
    assert ai_on_ai.match_score > backend_on_ai.match_score
    assert {normalize_skill(skill) for skill in backend_on_backend.matched_skills} != {
        normalize_skill(skill) for skill in ai_on_backend.matched_skills
    }


def _stored_job(job_id: str, title: str, description: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=job_id,
        title=title,
        description=description,
        apply_url=f"https://boards.greenhouse.io/acme/jobs/{job_id}",
        company="Acme",
        location="Remote",
        department=None,
        employment_type=None,
        requirements=None,
        remote=True,
        posted_at=None,
    )


def _parsed_document(user_id: ObjectId, parsed: ParsedResumeInput) -> SimpleNamespace:
    return SimpleNamespace(
        user_id=user_id,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        skills=parsed.skills,
        experience=[
            SimpleNamespace(
                title=item.title,
                company=item.company,
                start_date=item.start_date,
                end_date=item.end_date,
                description=item.description,
            )
            for item in parsed.experience
        ],
        projects=[
            SimpleNamespace(
                name=item.name,
                technologies=item.technologies,
                description=item.description,
            )
            for item in parsed.projects
        ],
        education=[
            SimpleNamespace(
                institution=item.institution,
                degree=item.degree,
                field=item.field,
            )
            for item in parsed.education
        ],
        summary=parsed.summary,
        raw_text=parsed.raw_text,
    )


class _MatchMocks:
    def __init__(self) -> None:
        self.get_by_id = AsyncMock()
        self.get_primary = AsyncMock(return_value=None)
        self.get_parsed = AsyncMock()
        self.watermark = AsyncMock(return_value=(0, datetime(2026, 6, 1, tzinfo=UTC)))
        self.list_active = AsyncMock(return_value=[])
        self.freshness_sample = AsyncMock(return_value=None)
        self.page = AsyncMock(return_value=([], 0))
        self.replace = AsyncMock()
        self.publish = patch(
            "app.services.jobs.match_service.publish_job_match_requested",
        )

    def apply_read(self):
        return (
            patch("app.services.jobs.match_service.ResumeRepository.get_by_id", self.get_by_id),
            patch(
                "app.services.jobs.match_service.ResumeRepository.get_primary_for_user",
                self.get_primary,
            ),
            patch(
                "app.services.jobs.match_service.ParsedResumeRepository.get_by_resume_id",
                self.get_parsed,
            ),
            patch(
                "app.services.jobs.match_service.JobRepository.matching_watermark",
                self.watermark,
            ),
            patch(
                "app.services.jobs.match_service.JobMatchRepository.freshness_sample",
                self.freshness_sample,
            ),
            patch("app.services.jobs.match_service.JobMatchRepository.page", self.page),
            self.publish,
        )

    def apply_rebuild(self):
        return (
            patch("app.services.jobs.match_service.ResumeRepository.get_by_id", self.get_by_id),
            patch(
                "app.services.jobs.match_service.ParsedResumeRepository.get_by_resume_id",
                self.get_parsed,
            ),
            patch("app.services.jobs.match_service.JobRepository.list_active", self.list_active),
            patch(
                "app.services.jobs.match_service.JobRepository.matching_watermark",
                self.watermark,
            ),
            patch(
                "app.services.jobs.match_service.JobMatchRepository.replace_for_resume",
                self.replace,
            ),
        )


async def _match(mocks: _MatchMocks, **kwargs: object):
    patches = mocks.apply_read()
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        return await JobMatchService.match_jobs(**kwargs)  # type: ignore[arg-type]


async def _rebuild(mocks: _MatchMocks, resume_id: object):
    patches = mocks.apply_rebuild()
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        return await JobMatchService.rebuild(str(resume_id))


def _owned_resume(
    user_id: ObjectId,
    *,
    status: ResumeStatus = ResumeStatus.PARSED,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=ObjectId(),
        user_id=user_id,
        status=status,
        is_primary=True,
    )


@pytest.mark.asyncio
async def test_match_threshold_filtering() -> None:
    user_id = ObjectId()
    resume = _owned_resume(user_id)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume
    mocks.get_parsed.return_value = _parsed_document(user_id, _backend_profile())
    mocks.list_active.return_value = [
        _stored_job("strong", "Backend Engineer", BACKEND_JD),
        _stored_job("mobile", "iOS Engineer", IOS_JD),
    ]
    mocks.watermark.return_value = (2, datetime(2026, 6, 1, tzinfo=UTC))

    matched, analyzed = await _rebuild(mocks, resume.id)
    assert analyzed == 2
    assert len(matched) == 1
    assert matched[0].job_id == "strong"
    assert matched[0].match_score >= 60
    mocks.list_active.assert_awaited()


@pytest.mark.asyncio
async def test_match_pagination() -> None:
    user_id = ObjectId()
    resume = _owned_resume(user_id)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume
    mocks.get_parsed.return_value = _parsed_document(user_id, _backend_profile())
    mocks.list_active.return_value = [
        _stored_job("b", "Backend Engineer", BACKEND_JD),
        _stored_job("a", "Backend Engineer Platform", BACKEND_JD),
        _stored_job("c", "Senior Backend Engineer", BACKEND_JD),
        _stored_job("ios-1", "iOS Engineer", IOS_JD),
        _stored_job("ios-2", "iOS Engineer", IOS_JD),
    ]
    mocks.watermark.return_value = (5, datetime(2026, 6, 1, tzinfo=UTC))

    matched, analyzed = await _rebuild(mocks, resume.id)
    assert analyzed == 5
    assert len(matched) == 3
    page_items = matched[2:4]
    assert len(page_items) == 1


@pytest.mark.asyncio
async def test_multiple_resumes_for_same_user_return_different_jobs() -> None:
    user_id = ObjectId()
    backend_resume = _owned_resume(user_id)
    ai_resume = _owned_resume(user_id)
    jobs = [
        _stored_job("backend", "Backend Engineer", BACKEND_JD),
        _stored_job("ai", "AI Engineer", AI_JD),
    ]

    async def run(resume: SimpleNamespace, parsed: ParsedResumeInput):
        mocks = _MatchMocks()
        mocks.get_by_id.return_value = resume
        mocks.get_parsed.return_value = _parsed_document(user_id, parsed)
        mocks.list_active.return_value = jobs
        mocks.watermark.return_value = (2, datetime(2026, 6, 1, tzinfo=UTC))
        matched, _analyzed = await _rebuild(mocks, resume.id)
        assert mocks.replace.await_args.kwargs["resume_id"] == resume.id
        return matched

    backend_matches = await run(backend_resume, _backend_profile())
    ai_matches = await run(ai_resume, _ai_profile())
    assert [job.job_id for job in backend_matches] == ["backend"]
    assert [job.job_id for job in ai_matches] == ["ai"]
    assert backend_matches[0].match_score != ai_matches[0].match_score


@pytest.mark.asyncio
async def test_other_users_resume_is_rejected() -> None:
    owner_id = ObjectId()
    caller_id = ObjectId()
    resume = _owned_resume(owner_id)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume

    with pytest.raises(AppException) as exc:
        await _match(
            mocks,
            user_id=caller_id,
            resume_id=str(resume.id),
            page=1,
            page_size=20,
        )
    assert exc.value.status_code == 404
    assert exc.value.code == "NOT_FOUND"
    mocks.list_active.assert_not_awaited()
    mocks.get_parsed.assert_not_awaited()


@pytest.mark.asyncio
async def test_unparsed_resume_is_rejected() -> None:
    user_id = ObjectId()
    resume = _owned_resume(user_id, status=ResumeStatus.PARSING)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume

    with pytest.raises(AppException) as exc:
        await _match(
            mocks,
            user_id=user_id,
            resume_id=str(resume.id),
            page=1,
            page_size=20,
        )
    assert exc.value.status_code == 409
    assert exc.value.code == "RESUME_NOT_PARSED"
    mocks.get_parsed.assert_not_awaited()


@pytest.mark.asyncio
async def test_parsed_status_without_profile_is_rejected() -> None:
    user_id = ObjectId()
    resume = _owned_resume(user_id)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume
    mocks.get_parsed.return_value = None

    with pytest.raises(AppException) as exc:
        await _match(
            mocks,
            user_id=user_id,
            resume_id=str(resume.id),
            page=1,
            page_size=20,
        )
    assert exc.value.code == "RESUME_NOT_PARSED"


@pytest.mark.asyncio
async def test_missing_primary_resume_asks_user_to_select_one() -> None:
    mocks = _MatchMocks()
    mocks.get_primary.return_value = None

    with pytest.raises(AppException) as exc:
        await _match(mocks, user_id=ObjectId(), resume_id=None, page=1, page_size=20)
    assert exc.value.status_code == 400
    assert exc.value.code == "RESUME_REQUIRED"
    mocks.get_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_explicit_resume_id_overrides_primary() -> None:
    user_id = ObjectId()
    selected = _owned_resume(user_id)
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = selected
    mocks.get_parsed.return_value = _parsed_document(user_id, _backend_profile())
    mocks.watermark.return_value = (1, datetime(2026, 6, 1, tzinfo=UTC))
    mocks.page.return_value = ([], 0)

    response = await _match(
        mocks,
        user_id=user_id,
        resume_id=str(selected.id),
        page=1,
        page_size=20,
    )
    assert response.resume_id == str(selected.id)
    assert response.scoring is True
    mocks.get_primary.assert_not_awaited()
    mocks.list_active.assert_not_awaited()


@pytest.mark.asyncio
async def test_fresh_cache_skips_rescoring() -> None:
    user_id = ObjectId()
    resume = _owned_resume(user_id)
    collected_at = datetime(2026, 6, 1, tzinfo=UTC)
    cached = SimpleNamespace(
        job_id=str(ObjectId()),
        title="Backend Engineer",
        company="Acme",
        location="Remote",
        remote=True,
        posted_at=None,
        url="https://boards.greenhouse.io/acme/jobs/1",
        match_score=91,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Kubernetes"],
        matched_role=True,
        experience_match=True,
        project_matches=["FastAPI"],
        match_reasons=["Strong skill overlap on Python, FastAPI"],
        active_job_count=40,
        profile_updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        latest_job_collected_at=collected_at,
    )
    mocks = _MatchMocks()
    mocks.get_by_id.return_value = resume
    mocks.get_parsed.return_value = _parsed_document(user_id, _backend_profile())
    mocks.freshness_sample.return_value = cached
    mocks.page.return_value = ([cached], 1)
    mocks.watermark.return_value = (40, collected_at)

    response = await _match(
        mocks,
        user_id=user_id,
        resume_id=str(resume.id),
        page=1,
        page_size=20,
    )
    mocks.list_active.assert_not_awaited()
    mocks.replace.assert_not_awaited()
    assert response.scoring is False
    assert response.total_jobs_analyzed == 40
    assert response.total_matched_jobs == 1
    assert response.jobs[0].match_score == 91
    assert response.jobs[0].job_id == cached.job_id
