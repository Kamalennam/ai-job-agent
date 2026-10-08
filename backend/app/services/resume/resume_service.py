from beanie import PydanticObjectId
from fastapi import UploadFile

from app.config import get_settings
from app.constants import ResumeStatus
from app.core.exceptions import AppException
from app.events.resume_uploaded import publish as publish_resume_uploaded
from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.parsed_resume_repository import ParsedResumeRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.auth import MessageResponse
from app.schemas.resume import (
    EducationDTO,
    ExperienceDTO,
    ParsedResumeResponse,
    ProjectDTO,
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeResponse,
)
from app.services.resume.parse_errors import public_parse_error
from app.services.resume.resume_storage import ResumeStorageService


class ResumeService:
    @staticmethod
    async def upload(
        user_id: PydanticObjectId,
        file: UploadFile,
        is_primary: bool = False,
    ) -> ResumeResponse:
        settings = get_settings()
        ResumeService._validate_upload(file)

        content = await file.read()
        max_bytes = settings.max_resume_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise AppException(
                400,
                "VALIDATION_ERROR",
                f"File exceeds maximum size of {settings.max_resume_size_mb}MB",
            )

        if is_primary:
            await ResumeRepository.clear_primary_for_user(user_id)

        relative_path, _ = ResumeStorageService.save(str(user_id), content)
        public_url = ResumeStorageService.build_public_url(relative_path)

        resume = Resume(
            user_id=user_id,
            filename=file.filename or relative_path.rsplit("/", 1)[-1],
            file_path=relative_path,
            file_url=public_url,
            file_size=len(content),
            mime_type=file.content_type or "application/pdf",
            status=ResumeStatus.PENDING,
            is_primary=is_primary,
            parse_progress=0,
            parse_stage="queued",
        )
        resume = await ResumeRepository.create(resume)

        publish_resume_uploaded(str(resume.id), str(user_id))

        return ResumeService._to_response(resume)

    @staticmethod
    async def list_resumes(user_id: PydanticObjectId) -> ResumeListResponse:
        resumes = await ResumeRepository.list_by_user(user_id)
        items = [ResumeService._to_response(resume) for resume in resumes]
        return ResumeListResponse(items=items, total=len(items))

    @staticmethod
    async def delete_resume(user_id: PydanticObjectId, resume_id: str) -> MessageResponse:
        resume = await ResumeService._get_owned_resume(user_id, resume_id)
        await ParsedResumeRepository.delete_by_resume_id(resume.id)
        await JobMatchRepository.delete_for_resume(resume.id)
        if resume.file_path:
            ResumeStorageService.delete(resume.file_path)
        await ResumeRepository.delete(resume)
        return MessageResponse(message="Resume deleted")

    @staticmethod
    async def get_resume(user_id: PydanticObjectId, resume_id: str) -> ResumeDetailResponse:
        resume = await ResumeService._get_owned_resume(user_id, resume_id)
        parsed = await ParsedResumeRepository.get_by_resume_id(resume.id)
        return ResumeService._to_detail_response(resume, parsed)

    @staticmethod
    def _validate_upload(file: UploadFile) -> None:
        settings = get_settings()
        filename = (file.filename or "").lower()
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        allowed = {ext.strip().lower() for ext in settings.allowed_resume_extensions.split(",")}

        if extension not in allowed:
            raise AppException(
                400,
                "INVALID_FILE_TYPE",
                f"Allowed file types: {', '.join(sorted(allowed))}",
            )

        if file.content_type and file.content_type != "application/pdf":
            raise AppException(400, "INVALID_FILE_TYPE", "Only PDF uploads are supported")

    @staticmethod
    async def _get_owned_resume(user_id: PydanticObjectId, resume_id: str) -> Resume:
        resume = await ResumeRepository.get_by_id(resume_id)
        if not resume or resume.user_id != user_id:
            raise AppException(404, "NOT_FOUND", "Resume not found")
        return resume

    @staticmethod
    def _build_file_url(resume: Resume) -> str | None:
        if resume.file_url:
            return resume.file_url
        if resume.file_path:
            return ResumeStorageService.build_public_url(resume.file_path)
        return None

    @staticmethod
    def _to_response(resume: Resume) -> ResumeResponse:
        return ResumeResponse(
            id=str(resume.id),
            filename=resume.filename,
            file_url=ResumeService._build_file_url(resume),
            status=resume.status,
            is_primary=resume.is_primary,
            parse_progress=resume.parse_progress,
            parse_stage=resume.parse_stage,
            created_at=resume.created_at,
        )

    @staticmethod
    def _to_detail_response(
        resume: Resume,
        parsed: ParsedResume | None,
    ) -> ResumeDetailResponse:
        parsed_response = None
        if parsed:
            parsed_response = ParsedResumeResponse(
                id=str(parsed.id),
                name=parsed.name,
                email=parsed.email,
                phone=parsed.phone,
                skills=parsed.skills,
                experience=[
                    ExperienceDTO.model_validate(item.model_dump()) for item in parsed.experience
                ],
                projects=[
                    ProjectDTO.model_validate(item.model_dump()) for item in parsed.projects
                ],
                education=[
                    EducationDTO.model_validate(item.model_dump()) for item in parsed.education
                ],
                summary=parsed.summary,
                raw_text=parsed.raw_text,
                parser_version=parsed.parser_version,
                parsed_at=parsed.parsed_at,
            )

        return ResumeDetailResponse(
            id=str(resume.id),
            filename=resume.filename,
            file_url=ResumeService._build_file_url(resume),
            status=resume.status,
            is_primary=resume.is_primary,
            parse_progress=resume.parse_progress,
            parse_stage=resume.parse_stage,
            parse_error=public_parse_error(resume.parse_error),
            parsed_resume=parsed_response,
            created_at=resume.created_at,
        )
