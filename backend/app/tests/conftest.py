import os

import pytest


@pytest.fixture(autouse=True)
def _required_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide minimal required settings for tests that load Settings."""
    defaults = {
        "APP_ENV": "development",
        "APP_SECRET_KEY": "test-app-secret-key-32chars-minimum",
        "API_BASE_URL": "http://localhost:8000",
        "CORS_ORIGINS": "http://localhost:5173",
        "MONGODB_URI": "mongodb://localhost:27017",
        "MONGODB_DB_NAME": "ai_job_agent_test",
        "REDIS_URL": "redis://localhost:6379/0",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
        "JWT_SECRET_KEY": "test-jwt-secret-key-32chars-minimum",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
        "FRONTEND_BASE_URL": "http://localhost:5173",
        "STORAGE_ROOT": "storage",
        "RESUME_STORAGE_DIR": "resumes",
    }
    for key, value in defaults.items():
        if key not in os.environ:
            monkeypatch.setenv(key, value)

    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
