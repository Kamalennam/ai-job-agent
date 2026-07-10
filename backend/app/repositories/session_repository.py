from datetime import UTC, datetime

from app.models.session import Session
from beanie import PydanticObjectId


class SessionRepository:
    @staticmethod
    async def create(session: Session) -> Session:
        return await session.insert()

    @staticmethod
    async def get_by_refresh_hash(refresh_token_hash: str) -> Session | None:
        return await Session.find_one(
            Session.refresh_token_hash == refresh_token_hash,
            Session.revoked == False,  # noqa: E712
        )

    @staticmethod
    async def save(session: Session) -> Session:
        await session.save()
        return session

    @staticmethod
    async def revoke(session: Session) -> None:
        session.revoked = True
        await session.save()

    @staticmethod
    async def revoke_all_for_user(user_id: PydanticObjectId) -> None:
        await Session.find(
            Session.user_id == user_id,
            Session.revoked == False,  # noqa: E712
        ).update({"$set": {"revoked": True}})

    @staticmethod
    async def delete_expired(before: datetime | None = None) -> None:
        cutoff = before or datetime.now(UTC)
        await Session.find(Session.expires_at < cutoff).delete()
