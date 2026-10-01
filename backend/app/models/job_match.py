from datetime import UTC, datetime

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class JobMatch(Document):
    """Cached score for one resume against one job.

    Rows are keyed by resume_id and job_id, so two resumes never share a score.
    """

    user_id: Indexed(PydanticObjectId)
    resume_id: Indexed(PydanticObjectId)
    job_id: Indexed(PydanticObjectId)
    match_score: int
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matched_role: bool = False
    experience_match: bool = False
    project_matches: list[str] = Field(default_factory=list)
    match_reasons: list[str] = Field(default_factory=list)
    title: str
    company: str
    location: str | None = None
    url: str
    remote: bool | None = None
    posted_at: datetime | None = None
    profile_updated_at: datetime
    active_job_count: int
    latest_job_collected_at: datetime | None = None
    min_score: int
    scorer_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "job_matches"
        indexes = [
            IndexModel(
                [("resume_id", ASCENDING), ("job_id", ASCENDING)],
                unique=True,
                name="resume_id_1_job_id_1",
            ),
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("resume_id", ASCENDING),
                    ("match_score", DESCENDING),
                ],
                name="user_id_1_resume_id_1_match_score_-1",
            ),
        ]
