from datetime import UTC, datetime

from app.models.resume import Resume
from beanie import PydanticObjectId


class ResumeRepository:
    @staticmethod
    async def get_by_id(resume_id: str | PydanticObjectId) -> Resume | None:
        return await Resume.get(PydanticObjectId(str(resume_id)))

    @staticmethod
    async def get_primary_for_user(user_id: PydanticObjectId) -> Resume | None:
        return await Resume.find_one(
            Resume.user_id == user_id,
            Resume.is_primary == True,  # noqa: E712
        )

    @staticmethod
    async def list_by_user(user_id: PydanticObjectId) -> list[Resume]:
        return await Resume.find(Resume.user_id == user_id).sort(-Resume.created_at).to_list()

    @staticmethod
    async def create(resume: Resume) -> Resume:
        return await resume.insert()

    @staticmethod
    async def save(resume: Resume) -> Resume:
        resume.updated_at = datetime.now(UTC)
        await resume.save()
        return resume

    @staticmethod
    async def clear_primary_for_user(user_id: PydanticObjectId) -> None:
        await Resume.find(
            Resume.user_id == user_id,
            Resume.is_primary == True,  # noqa: E712
        ).update({"$set": {"is_primary": False}})

    @staticmethod
    async def delete(resume: Resume) -> None:
        await resume.delete()
