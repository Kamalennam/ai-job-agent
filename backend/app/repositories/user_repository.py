from datetime import UTC, datetime

from app.models.user import User
from beanie import PydanticObjectId


class UserRepository:
    @staticmethod
    async def get_by_id(user_id: str | PydanticObjectId) -> User | None:
        return await User.get(PydanticObjectId(str(user_id)))

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        return await User.find_one(User.email == email.lower())

    @staticmethod
    async def get_by_verification_token_hash(token_hash: str) -> User | None:
        return await User.find_one(User.verification_token_hash == token_hash)

    @staticmethod
    async def create(user: User) -> User:
        return await user.insert()

    @staticmethod
    async def save(user: User) -> User:
        user.updated_at = datetime.now(UTC)
        await user.save()
        return user
