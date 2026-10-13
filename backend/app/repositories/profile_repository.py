from datetime import UTC, datetime

from app.models.profile import Profile
from beanie import PydanticObjectId


class ProfileRepository:
    @staticmethod
    async def create(profile: Profile) -> Profile:
        return await profile.insert()

    @staticmethod
    async def get_by_user_id(user_id: str | PydanticObjectId) -> Profile | None:
        return await Profile.find_one(Profile.user_id == PydanticObjectId(str(user_id)))

    @staticmethod
    async def save(profile: Profile) -> Profile:
        profile.updated_at = datetime.now(UTC)
        await profile.save()
        return profile
