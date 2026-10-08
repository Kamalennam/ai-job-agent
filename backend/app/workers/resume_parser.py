import asyncio

from loguru import logger

from app.ai.ollama_client import OllamaError
from app.ai.resume_extraction.extract import PROMPT_VERSION, extract_structured_resume
from app.config import get_settings
from app.constants import ResumeStatus
from app.db.client import close_db, connect_db
from app.models.parsed_resume import Education, Experience, ParsedResume, Project
from app.models.resume import Resume
from app.repositories.parsed_resume_repository import ParsedResumeRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.resume.parse_errors import USER_PARSE_EMPTY, USER_PARSE_FAILED
from app.services.resume.parse_progress import analysis_progress
from app.services.resume.resume_storage import ResumeStorageService
from app.utils.resume_extractor import PARSER_VERSION, extract_text_from_pdf
from app.workers.celery import celery


@celery.task(name="parse_resume", queue="resume", ignore_result=True)
def parse_resume(resume_id: str) -> None:
    asyncio.run(_parse_resume_async(resume_id))


async def parse_resume_now(resume_id: str) -> None:
    """Parse using the caller's event loop and its existing database connection."""
    await _parse_resume(resume_id)


async def _parse_resume_async(resume_id: str) -> None:
    await connect_db()
    try:
        await _parse_resume(resume_id)
    finally:
        await close_db()


class _ResumeRemoved(Exception):
    """Raised when the user deletes a resume while parsing is still running."""


async def _report(
    resume_id: str,
    progress: int,
    stage: str,
    *,
    status: ResumeStatus = ResumeStatus.PARSING,
    error: str | None = None,
) -> Resume | None:
    resume = await ResumeRepository.get_by_id(resume_id)
    if not resume:
        return None
    resume.status = status
    resume.parse_progress = progress
    resume.parse_stage = stage
    resume.parse_error = error
    await ResumeRepository.save(resume)
    return resume


async def _parse_resume(resume_id: str) -> None:
    resume = await _report(resume_id, 8, "reading")
    if not resume:
        logger.warning("Resume {} not found for parsing", resume_id)
        return

    file_path = ResumeStorageService.resolve_path(resume.file_path)
    settings = get_settings()
    last_progress = 8

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        raw_text = extract_text_from_pdf(file_path)
        if not raw_text.strip():
            raise ValueError("No text could be extracted from the PDF")

        if await _report(resume_id, 28, "extracting") is None:
            return

        async def on_text(received_chars: int) -> None:
            nonlocal last_progress
            progress = analysis_progress(received_chars)
            if progress < last_progress + 2:
                return
            if await _report(resume_id, progress, "analyzing") is None:
                raise _ResumeRemoved()
            last_progress = progress

        extraction = await extract_structured_resume(raw_text, on_text=on_text)
        if await _report(resume_id, 95, "saving") is None:
            return

        current = await ResumeRepository.get_by_id(resume_id)
        if not current:
            return

        existing = await ParsedResumeRepository.get_by_resume_id(current.id)
        if existing:
            await ParsedResumeRepository.delete_by_resume_id(current.id)

        parsed = ParsedResume(
            resume_id=current.id,
            user_id=current.user_id,
            name=extraction.name,
            email=extraction.email,
            phone=extraction.phone,
            skills=[skill.strip() for skill in extraction.skills if skill.strip()],
            experience=[
                Experience.model_validate(item.model_dump()) for item in extraction.experience
            ],
            projects=[Project.model_validate(item.model_dump()) for item in extraction.projects],
            education=[
                Education.model_validate(item.model_dump()) for item in extraction.education
            ],
            summary=extraction.summary,
            raw_text=raw_text,
            parser_version=f"{PARSER_VERSION}+{PROMPT_VERSION}+{settings.ollama_model}",
        )
        await ParsedResumeRepository.create(parsed)

        await _report(resume_id, 100, "complete", status=ResumeStatus.PARSED)
        from app.events.job_match_requested import publish as publish_job_match_requested

        publish_job_match_requested(resume_id)
        logger.info(
            "Parsed resume {} via Ollama ({} skills, {} jobs, {} projects)",
            resume_id,
            len(parsed.skills),
            len(parsed.experience),
            len(parsed.projects),
        )
    except _ResumeRemoved:
        logger.info("Resume {} was deleted during parsing", resume_id)
    except OllamaError as exc:
        logger.error("Ollama extraction failed for resume {}: {}", resume_id, exc)
        await _report(
            resume_id,
            last_progress,
            "failed",
            status=ResumeStatus.FAILED,
            error=USER_PARSE_FAILED,
        )
    except ValueError as exc:
        logger.warning("Resume {} could not be read: {}", resume_id, exc)
        message = USER_PARSE_EMPTY if "no text" in str(exc).lower() else USER_PARSE_FAILED
        await _report(
            resume_id,
            last_progress,
            "failed",
            status=ResumeStatus.FAILED,
            error=message,
        )
    except Exception:
        logger.exception("Failed to parse resume {}", resume_id)
        await _report(
            resume_id,
            last_progress,
            "failed",
            status=ResumeStatus.FAILED,
            error=USER_PARSE_FAILED,
        )
