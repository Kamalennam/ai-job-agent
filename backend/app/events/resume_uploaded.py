"""
Event: resume_uploaded

Published when a user uploads a resume file.
Triggers resume_parser worker.

Publisher: ResumeService.upload()
Consumer:  workers/resume_parser.py
"""

from dataclasses import dataclass

from loguru import logger

from app.workers.resume_parser import parse_resume


@dataclass
class ResumeUploadedPayload:
    resume_id: str
    user_id: str


def publish(resume_id: str, user_id: str) -> None:
    """Publish resume_uploaded event → queue resume_parser worker."""
    try:
        parse_resume.delay(resume_id)
    except Exception as exc:
        logger.warning(
            "Resume {} saved but parse job was not queued. Start Redis + Celery worker: {}",
            resume_id,
            exc,
        )
