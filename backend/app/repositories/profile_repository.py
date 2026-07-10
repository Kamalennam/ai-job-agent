from app.models.profile import Profile


class ProfileRepository:
    @staticmethod
    async def create(profile: Profile) -> Profile:
        return await profile.insert()
