"""
Event: application_submitted

Published when user approves apply OR scheduler triggers ATS queue.
Triggers ats_apply worker.

Publisher: ApplicationService.apply() / scheduler
Consumer:  workers/ats_apply.py
"""

from dataclasses import dataclass

from app.workers.ats_apply import apply_to_job


@dataclass
class ApplicationSubmittedPayload:
    application_id: str
    user_id: str


def publish(application_id: str, user_id: str) -> None:
    """Publish application_submitted event → queue ats_apply worker."""
    apply_to_job.delay(application_id)
