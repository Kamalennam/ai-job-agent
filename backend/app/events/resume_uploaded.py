"""
Event: resume_uploaded

Published when a user uploads a resume file.
Triggers resume_parser worker.

Publisher: ResumeService.upload()
Consumer:  workers/resume_parser.py
"""

import asyncio
from dataclasses import dataclass

from loguru import logger

from app.workers.resume_parser import parse_resume, parse_resume_now


@dataclass
class ResumeUploadedPayload:
    resume_id: str
    user_id: str


def publish(resume_id: str, user_id: str) -> None:
    """Publish resume_uploaded event → queue resume_parser worker.

    When Redis is down (typical local dev without Docker), run the same
    parser in this process so the upload does not stay pending forever.
    """
    try:
        parse_resume.delay(resume_id)
    except Exception as exc:
        logger.warning(
            "Resume {} could not be queued ({}). Parsing in-process.",
            resume_id,
            exc,
        )
        _parse_in_process(resume_id)


def _parse_in_process(resume_id: str) -> None:
    """Run the parser on the API event loop, reusing the open Mongo connection."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.error("Cannot parse resume {} in-process: no running event loop", resume_id)
        return

    task = loop.create_task(parse_resume_now(resume_id))
    task.add_done_callback(_log_in_process_failure)


def _log_in_process_failure(task: asyncio.Task[None]) -> None:
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        logger.opt(exception=error).error("In-process resume parse failed")
