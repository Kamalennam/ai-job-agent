"""
Event: jobs_collected

Published when job_scraper worker finishes collecting jobs.
Triggers job_matcher worker (Phase 9).
"""


def publish(count: int, sources: list[str]) -> None:
    if count <= 0:
        return
    from app.workers.job_matcher import score_all

    score_all.delay()
