import asyncio

from loguru import logger

from app.ai.ollama_client import OllamaError
from app.ai.resume_extraction.extract import PROMPT_VERSION, extract_structured_resume
from app.config import get_settings
from app.constants import ResumeStatus
from app.db.client import close_db, connect_db
from app.models.parsed_resume import Education, Experience, ParsedResume, Project
from app.repositories.parsed_resume_repository import ParsedResumeRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.resume.resume_storage import ResumeStorageService
from app.utils.resume_extractor import PARSER_VERSION, extract_text_from_pdf
from app.workers.celery import celery


@celery.task(name="parse_resume", queue="resume", ignore_result=True)
def parse_resume(resume_id: str) -> None:
    asyncio.run(_parse_resume_async(resume_id))


async def _parse_resume_async(resume_id: str) -> None:
    await connect_db()
    try:
        await _parse_resume(resume_id)
    finally:
        await close_db()


async def _parse_resume(resume_id: str) -> None:
    resume = await ResumeRepository.get_by_id(resume_id)
    if not resume:
        logger.warning("Resume {} not found for parsing", resume_id)
        return

    resume.status = ResumeStatus.PARSING
    resume.parse_error = None
    await ResumeRepository.save(resume)

    file_path = ResumeStorageService.resolve_path(resume.file_path)
    settings = get_settings()

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        raw_text = extract_text_from_pdf(file_path)
        if not raw_text.strip():
            raise ValueError("No text could be extracted from the PDF")

        extraction = await extract_structured_resume(raw_text)

        existing = await ParsedResumeRepository.get_by_resume_id(resume.id)
        if existing:
            await ParsedResumeRepository.delete_by_resume_id(resume.id)

        parsed = ParsedResume(
            resume_id=resume.id,
            user_id=resume.user_id,
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

        resume.status = ResumeStatus.PARSED
        resume.parse_error = None
        await ResumeRepository.save(resume)
        logger.info(
            "Parsed resume {} via Ollama ({} skills, {} jobs, {} projects)",
            resume_id,
            len(parsed.skills),
            len(parsed.experience),
            len(parsed.projects),
        )
    except OllamaError as exc:
        resume.status = ResumeStatus.FAILED
        resume.parse_error = str(exc)
        await ResumeRepository.save(resume)
        logger.error("Ollama extraction failed for resume {}: {}", resume_id, exc)
    except Exception as exc:
        resume.status = ResumeStatus.FAILED
        resume.parse_error = str(exc)
        await ResumeRepository.save(resume)
        logger.exception("Failed to parse resume {}", resume_id)
