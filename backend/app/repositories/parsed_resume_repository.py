from datetime import UTC, datetime

from app.models.parsed_resume import ParsedResume
from beanie import PydanticObjectId


class ParsedResumeRepository:
    @staticmethod
    async def get_by_resume_id(resume_id: PydanticObjectId) -> ParsedResume | None:
        return await ParsedResume.find_one(ParsedResume.resume_id == resume_id)

    @staticmethod
    async def create(parsed_resume: ParsedResume) -> ParsedResume:
        return await parsed_resume.insert()

    @staticmethod
    async def save(parsed_resume: ParsedResume) -> ParsedResume:
        parsed_resume.updated_at = datetime.now(UTC)
        await parsed_resume.save()
        return parsed_resume

    @staticmethod
    async def delete_by_resume_id(resume_id: PydanticObjectId) -> None:
        existing = await ParsedResumeRepository.get_by_resume_id(resume_id)
        if existing:
            await existing.delete()
