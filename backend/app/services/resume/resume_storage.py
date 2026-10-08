import uuid
from pathlib import Path

from app.config import get_settings


class ResumeStorageService:
    @staticmethod
    def storage_root() -> Path:
        return get_settings().resolved_resume_storage_dir

    @staticmethod
    def save(user_id: str, content: bytes, extension: str = "pdf") -> tuple[str, Path]:
        stored_name = f"{uuid.uuid4().hex}.{extension}"
        relative_path = f"{user_id}/{stored_name}"
        absolute_path = ResumeStorageService.storage_root() / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return relative_path, absolute_path

    @staticmethod
    def resolve_path(relative_path: str) -> Path:
        return ResumeStorageService.storage_root() / relative_path

    @staticmethod
    def delete(relative_path: str) -> None:
        path = ResumeStorageService.resolve_path(relative_path)
        if path.is_file():
            path.unlink()

    @staticmethod
    def build_public_url(relative_path: str) -> str:
        return get_settings().build_resume_public_url(relative_path)
