"""
Event: email_sent

Published when recruiter_email worker successfully sends an email.
Triggers analytics and notification workers.

Publisher: workers/recruiter_email.py
Consumer:  workers/analytics.py, workers/notification.py
"""

from dataclasses import dataclass

from app.workers.analytics import record_email_sent
from app.workers.notification import notify_email_sent


@dataclass
class EmailSentPayload:
    email_id: str
    user_id: str
    recruiter_id: str
    application_id: str


def publish(email_id: str, user_id: str, recruiter_id: str, application_id: str) -> None:
    """Publish email_sent event → analytics + notification workers."""
    record_email_sent.delay(email_id, user_id)
    notify_email_sent.delay(user_id, email_id, application_id)
