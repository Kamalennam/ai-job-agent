from fastapi import UploadFile

from app.config import get_settings
from app.core.exceptions import AppException
from app.models.profile import Profile
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, UpdateProfileRequest
from app.services.profile.profile_image_storage import ProfileImageStorage

_STORED_EXTENSION = {"jpg": "jpg", "jpeg": "jpg", "png": "png", "webp": "webp"}
_CONTENT_TYPES = {
    "jpg": {"image/jpeg", "image/jpg", "image/pjpeg", "application/octet-stream"},
    "png": {"image/png", "application/octet-stream"},
    "webp": {"image/webp", "application/octet-stream"},
}


class ProfileService:
    @staticmethod
    async def get(user: User) -> ProfileResponse:
        profile = await ProfileService._require(user)
        return ProfileService._to_response(user, profile)

    @staticmethod
    async def update(user: User, data: UpdateProfileRequest) -> ProfileResponse:
        profile = await ProfileService._require(user)
        profile.full_name = data.full_name
        profile.headline = data.headline
        profile.location = data.location
        profile.linkedin_url = data.linkedin_url
        profile.bio = data.bio
        profile = await ProfileRepository.save(profile)
        return ProfileService._to_response(user, profile)

    @staticmethod
    async def upload_avatar(user: User, file: UploadFile) -> ProfileResponse:
        profile = await ProfileService._require(user)
        content, extension = await ProfileService._read_avatar(file)
        relative_path, _absolute = ProfileImageStorage.save(str(user.id), content, extension)
        previous_url = profile.avatar_url
        profile.avatar_url = ProfileImageStorage.build_public_url(relative_path)
        profile = await ProfileRepository.save(profile)
        if previous_url != profile.avatar_url:
            ProfileImageStorage.delete_owned_url(previous_url, str(user.id))
        return ProfileService._to_response(user, profile)

    @staticmethod
    async def remove_avatar(user: User) -> ProfileResponse:
        profile = await ProfileService._require(user)
        previous_url = profile.avatar_url
        profile.avatar_url = None
        profile = await ProfileRepository.save(profile)
        ProfileImageStorage.delete_owned_url(previous_url, str(user.id))
        return ProfileService._to_response(user, profile)

    @staticmethod
    async def _require(user: User) -> Profile:
        profile = await ProfileRepository.get_by_user_id(user.id)
        if not profile:
            raise AppException(404, "NOT_FOUND", "Profile not found")
        return profile

    @staticmethod
    async def _read_avatar(file: UploadFile) -> tuple[bytes, str]:
        settings = get_settings()
        filename = (file.filename or "").lower()
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
        allowed = {
            item.strip().lower()
            for item in settings.allowed_profile_image_extensions.split(",")
        }
        if extension not in allowed:
            raise AppException(400, "INVALID_FILE_TYPE", "Use a JPG, PNG, or WebP image")

        content = await file.read()
        if not content:
            raise AppException(400, "VALIDATION_ERROR", "Choose an image file")

        max_bytes = settings.max_profile_image_size_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise AppException(
                400,
                "VALIDATION_ERROR",
                f"Photo must be {settings.max_profile_image_size_mb} MB or smaller",
            )

        sniffed = _sniff_image(content)
        stored_extension = _STORED_EXTENSION.get(extension)
        if sniffed is None or sniffed != stored_extension:
            raise AppException(400, "INVALID_FILE_TYPE", "Use a JPG, PNG, or WebP image")

        content_type = (file.content_type or "").split(";", 1)[0].strip().lower()
        if content_type and content_type not in _CONTENT_TYPES[sniffed]:
            raise AppException(400, "INVALID_FILE_TYPE", "Use a JPG, PNG, or WebP image")
        return content, sniffed

    @staticmethod
    def _to_response(user: User, profile: Profile) -> ProfileResponse:
        return ProfileResponse(
            id=str(profile.id),
            email=user.email,
            email_verified=user.email_verified,
            full_name=profile.full_name,
            headline=profile.headline,
            location=profile.location,
            linkedin_url=profile.linkedin_url,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
        )


def _sniff_image(content: bytes) -> str | None:
    if content.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "webp"
    return None
