from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery = Celery(
    "ai_job_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "parse_resume": {"queue": "resume"},
        "collect_jobs": {"queue": "scraping"},
        "score_all": {"queue": "matching"},
        "score_resume": {"queue": "matching"},
    },
    beat_schedule={
        "collect-jobs-hourly": {
            "task": "collect_jobs",
            "schedule": crontab(minute=0),
            "options": {"queue": "scraping"},
        },
    },
)

celery.autodiscover_tasks(["app.workers"])

import app.workers.job_matcher  # noqa: E402, F401
import app.workers.job_scraper  # noqa: E402, F401
import app.workers.resume_parser  # noqa: E402, F401
