"""
Event: job_collection_requested

Published when a user manually triggers job collection from the API.
Triggers job_scraper worker.
"""

from app.workers.job_scraper import collect_jobs


def publish() -> None:
    collect_jobs.delay()
