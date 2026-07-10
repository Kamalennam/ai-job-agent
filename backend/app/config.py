from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class StorageProvider(str, Enum):
    LOCAL = "local"


class Settings(BaseSettings):
    """Application configuration loaded exclusively from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parents[2] / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "AI Job Agent"
    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    app_debug: bool = True
    app_secret_key: str = Field(..., min_length=8)
    api_v1_prefix: str = "/api/v1"
    api_base_url: str = Field(..., description="Public API origin without trailing slash")
    cors_origins: str = Field(..., description="Comma-separated allowed CORS origins")

    # --- MongoDB ---
    mongodb_uri: str = Field(...)
    mongodb_db_name: str = Field(...)

    # --- Redis / Celery ---
    redis_url: str = Field(...)
    celery_broker_url: str = Field(...)
    celery_result_backend: str = Field(...)

    # --- JWT ---
    jwt_secret_key: str = Field(..., min_length=8)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # --- Ollama ---
    ollama_base_url: str = Field(...)
    ollama_model: str = Field(...)
    ollama_embedding_model: str = Field(...)
    prompts_dir: str = "prompts"
    ollama_timeout_seconds: int = 120
    ollama_extraction_temperature: float = 0.3
    configs_dir: str = "configs"

    # --- Frontend ---
    frontend_base_url: str = Field(...)

    # --- Email (optional — verification links logged when SMTP is incomplete) ---
    email_verification_expire_hours: int = 24
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # --- Storage ---
    storage_provider: StorageProvider = StorageProvider.LOCAL
    storage_root: str = Field(...)
    resume_storage_dir: str = Field(...)
    generated_resume_dir: str = "generated-resumes"
    cover_letter_dir: str = "cover-letters"
    profile_image_dir: str = "profile-images"
    temp_dir: str = "temp"

    # --- Resume upload limits ---
    max_resume_size_mb: int = 10
    allowed_resume_extensions: str = "pdf"

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnvironment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.app_env == AppEnvironment.DEVELOPMENT

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _resolve_path(self, path_str: str) -> Path:
        path = Path(path_str)
        if path.is_absolute():
            return path
        return self._repo_root() / path

    def _resolve_storage_subdir(self, subdir: str) -> Path:
        return self._resolve_path(self.storage_root) / subdir

    @property
    def resolved_storage_root(self) -> Path:
        return self._resolve_path(self.storage_root)

    @property
    def resolved_resume_storage_dir(self) -> Path:
        return self._resolve_storage_subdir(self.resume_storage_dir)

    @property
    def resolved_generated_resume_dir(self) -> Path:
        return self._resolve_storage_subdir(self.generated_resume_dir)

    @property
    def resolved_cover_letter_dir(self) -> Path:
        return self._resolve_storage_subdir(self.cover_letter_dir)

    @property
    def resolved_profile_image_dir(self) -> Path:
        return self._resolve_storage_subdir(self.profile_image_dir)

    @property
    def resolved_temp_dir(self) -> Path:
        return self._resolve_storage_subdir(self.temp_dir)

    @property
    def resume_public_url_prefix(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/storage/resumes"

    def build_resume_public_url(self, relative_path: str) -> str:
        return f"{self.resume_public_url_prefix}/{relative_path.lstrip('/')}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def smtp_configured(self) -> bool:
        return bool(
            self.smtp_host
            and self.smtp_from_email
            and self.smtp_user
            and self.smtp_password
        )

    @property
    def resolved_prompts_dir(self) -> Path:
        return self._resolve_path(self.prompts_dir)

    @property
    def resolved_configs_dir(self) -> Path:
        return self._resolve_path(self.configs_dir)

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if not self.is_production:
            return self

        weak_markers = ("change-me", "changeme", "example", "placeholder")
        for field_name, value in (
            ("app_secret_key", self.app_secret_key),
            ("jwt_secret_key", self.jwt_secret_key),
        ):
            normalized = value.lower()
            if any(marker in normalized for marker in weak_markers) or len(value) < 32:
                raise ValueError(
                    f"{field_name} must be a strong secret (32+ characters) in production"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
