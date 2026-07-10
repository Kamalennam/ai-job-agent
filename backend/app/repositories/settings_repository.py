from app.models.settings import UserSettings


class SettingsRepository:
    @staticmethod
    async def create(settings: UserSettings) -> UserSettings:
        return await settings.insert()
