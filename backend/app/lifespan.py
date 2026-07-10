from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db.client import close_db, connect_db
from app.db.init_db import init_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    for storage_dir in (
        settings.resolved_storage_root,
        settings.resolved_resume_storage_dir,
        settings.resolved_generated_resume_dir,
        settings.resolved_cover_letter_dir,
        settings.resolved_profile_image_dir,
        settings.resolved_temp_dir,
    ):
        storage_dir.mkdir(parents=True, exist_ok=True)
    await connect_db()
    await init_indexes()
    yield
    await close_db()


def create_app() -> FastAPI:
    settings = get_settings()
    return FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
