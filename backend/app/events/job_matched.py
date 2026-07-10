"""
Event: job_matched

Published when job_matcher creates a high-score application match.
Triggers notification worker.

Publisher: workers/job_matcher.py
Consumer:  workers/notification.py
"""

from dataclasses import dataclass

from app.workers.notification import notify_match


@dataclass
class JobMatchedPayload:
    user_id: str
    application_id: str
    job_id: str
    score: float


def publish(user_id: str, application_id: str, job_id: str, score: float) -> None:
    """Publish job_matched event → queue notification worker."""
    notify_match.delay(user_id, application_id, job_id, score)
