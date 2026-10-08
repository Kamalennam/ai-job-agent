"""
Event: job_match_requested

Published when a resume needs its job scores rebuilt.
Triggers job_matcher.score_resume.

Publisher: JobMatchService.match_jobs(), resume_parser
Consumer:  workers/job_matcher.py
"""

import asyncio
import time

from loguru import logger

from app.events.broker import broker_reachable

_CLAIM_SECONDS = 120.0
_claimed_until: dict[str, float] = {}


def publish(resume_id: str) -> None:
    """Queue scoring. Never blocks the request on a full rescore.

    Hostinger queues the Celery worker. When Redis is down, the API process
    scores in the background and the HTTP call still returns immediately.
    """
    if not _claim(resume_id):
        return

    from app.workers.job_matcher import score_resume, score_resume_now

    if broker_reachable():
        try:
            score_resume.delay(resume_id)
            return
        except Exception as exc:
            logger.warning("Resume {} could not be queued for matching ({}).", resume_id, exc)

    _score_in_process(resume_id, score_resume_now)


def _claim(resume_id: str) -> bool:
    now = time.monotonic()
    if _claimed_until.get(resume_id, 0.0) > now:
        return False
    _claimed_until[resume_id] = now + _CLAIM_SECONDS
    return True


def _release(resume_id: str) -> None:
    _claimed_until.pop(resume_id, None)


def _score_in_process(resume_id: str, score_resume_now) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.error("Cannot match resume {} in-process: no running event loop", resume_id)
        _release(resume_id)
        return

    task = loop.create_task(score_resume_now(resume_id))
    task.add_done_callback(lambda done: _on_in_process_done(resume_id, done))


def _on_in_process_done(resume_id: str, task: asyncio.Task[None]) -> None:
    _release(resume_id)
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        logger.opt(exception=error).error("In-process job match failed for resume {}", resume_id)
