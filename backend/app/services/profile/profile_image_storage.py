import re
import uuid
from pathlib import Path

from app.config import get_settings

_STORED_NAME = re.compile(r"^[a-f0-9]{32}\.(jpg|png|webp)$")
_USER_FOLDER = re.compile(r"^[a-fA-F0-9]{24}$")


class ProfileImageStorage:
    @staticmethod
    def storage_root() -> Path:
        return get_settings().resolved_profile_image_dir

    @staticmethod
    def save(user_id: str, content: bytes, extension: str) -> tuple[str, Path]:
        if not _USER_FOLDER.fullmatch(user_id) or extension not in {"jpg", "png", "webp"}:
            raise ValueError("Invalid profile photo path")
        stored_name = f"{uuid.uuid4().hex}.{extension}"
        relative_path = f"{user_id}/{stored_name}"
        absolute_path = ProfileImageStorage.resolve_path(relative_path)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return relative_path, absolute_path

    @staticmethod
    def resolve_path(relative_path: str) -> Path:
        root = ProfileImageStorage.storage_root().resolve()
        path = (root / relative_path).resolve()
        if path != root and root not in path.parents:
            raise ValueError("Invalid profile photo path")
        return path

    @staticmethod
    def delete(relative_path: str) -> None:
        path = ProfileImageStorage.resolve_path(relative_path)
        if path.is_file():
            path.unlink()

    @staticmethod
    def build_public_url(relative_path: str) -> str:
        return get_settings().build_profile_image_public_url(relative_path)

    @staticmethod
    def delete_owned_url(url: str | None, user_id: str) -> None:
        relative = ProfileImageStorage.relative_from_public_url(url)
        if not relative:
            return
        owner, _name = relative.split("/", 1)
        if owner != user_id:
            return
        ProfileImageStorage.delete(relative)

    @staticmethod
    def relative_from_public_url(url: str | None) -> str | None:
        if not url:
            return None
        prefix = f"{get_settings().profile_image_public_url_prefix}/"
        if not url.startswith(prefix):
            return None
        relative = url[len(prefix) :].split("?", 1)[0]
        owner, _, filename = relative.partition("/")
        if not _USER_FOLDER.fullmatch(owner) or not _STORED_NAME.fullmatch(filename):
            return None
        if "/" in filename:
            return None
        return f"{owner}/{filename}"
