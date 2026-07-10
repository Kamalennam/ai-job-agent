from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config import get_settings
from app.models.company import Company
from app.models.job import Job
from app.models.parsed_resume import ParsedResume
from app.models.profile import Profile
from app.models.resume import Resume
from app.models.scheduler_log import SchedulerLog
from app.models.session import Session
from app.models.settings import UserSettings
from app.models.user import User

_client: AsyncMongoClient | None = None
_database: AsyncDatabase | None = None

DOCUMENT_MODELS = [
    User,
    Session,
    Profile,
    UserSettings,
    Resume,
    ParsedResume,
    Company,
    Job,
    SchedulerLog,
]


async def connect_db() -> None:
    global _client, _database
    settings = get_settings()
    _client = AsyncMongoClient(settings.mongodb_uri)
    _database = _client[settings.mongodb_db_name]
    await init_beanie(database=_database, document_models=DOCUMENT_MODELS)
    await _client.admin.command("ping")


async def close_db() -> None:
    global _client, _database
    if _client is not None:
        await _client.close()
    _client = None
    _database = None


def get_database() -> AsyncDatabase:
    if _database is None:
        raise RuntimeError("Database is not initialized")
    return _database
