import asyncio
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from starlette.datastructures import Headers, UploadFile

from app.config import get_settings
from app.core.exceptions import AppException
from app.services.profile.profile_image_storage import ProfileImageStorage
from app.services.profile.profile_service import ProfileService

USER_ID = "665a1b2c3d4e5f6789012345"
PNG = b"\x89PNG\r\n\x1a\n" + b"profile-photo"


def _user() -> SimpleNamespace:
    return SimpleNamespace(id=USER_ID, email="person@example.com", email_verified=True)


def _profile(**overrides: object) -> SimpleNamespace:
    data = {
        "id": "profile-1",
        "full_name": "Person Example",
        "headline": None,
        "location": None,
        "linkedin_url": None,
        "avatar_url": None,
        "bio": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def _upload(
    content: bytes,
    filename: str = "photo.png",
    content_type: str = "image/png",
) -> UploadFile:
    return UploadFile(
        BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def _use_storage(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("API_BASE_URL", "https://jobs.example.com")
    get_settings.cache_clear()


def test_save_writes_under_profile_images_and_builds_a_public_url(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)

    relative, absolute = ProfileImageStorage.save(USER_ID, PNG, "png")

    assert relative.startswith(f"{USER_ID}/")
    assert relative.endswith(".png")
    assert absolute.read_bytes() == PNG
    assert ProfileImageStorage.build_public_url(relative) == (
        f"https://jobs.example.com/storage/profile-images/{relative}"
    )
    get_settings.cache_clear()


def test_upload_avatar_stores_the_public_url(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)
    profile = _profile()

    async def save(item):
        return item

    async def run() -> None:
        with (
            patch(
                "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
                new=AsyncMock(return_value=profile),
            ),
            patch(
                "app.services.profile.profile_service.ProfileRepository.save",
                side_effect=save,
            ),
        ):
            result = await ProfileService.upload_avatar(_user(), _upload(PNG))
        assert result.avatar_url.startswith(
            f"https://jobs.example.com/storage/profile-images/{USER_ID}/"
        )
        assert result.avatar_url.endswith(".png")
        stored = ProfileImageStorage.relative_from_public_url(result.avatar_url)
        assert stored is not None
        assert ProfileImageStorage.resolve_path(stored).is_file()

    asyncio.run(run())
    get_settings.cache_clear()


def test_replacing_a_photo_removes_the_previous_file(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)
    profile = _profile()

    async def save(item):
        return item

    async def run() -> None:
        with (
            patch(
                "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
                new=AsyncMock(return_value=profile),
            ),
            patch(
                "app.services.profile.profile_service.ProfileRepository.save",
                side_effect=save,
            ),
        ):
            first = await ProfileService.upload_avatar(_user(), _upload(PNG))
            first_path = ProfileImageStorage.relative_from_public_url(first.avatar_url)
            second = await ProfileService.upload_avatar(
                _user(),
                _upload(b"\xff\xd8\xffphoto", "me.jpg", "image/jpeg"),
            )
        assert first_path is not None
        assert not ProfileImageStorage.resolve_path(first_path).exists()
        second_path = ProfileImageStorage.relative_from_public_url(second.avatar_url)
        assert second_path is not None
        assert ProfileImageStorage.resolve_path(second_path).is_file()

    asyncio.run(run())
    get_settings.cache_clear()


def test_remove_avatar_clears_the_url_and_file(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)
    profile = _profile()

    async def save(item):
        return item

    async def run() -> None:
        with (
            patch(
                "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
                new=AsyncMock(return_value=profile),
            ),
            patch(
                "app.services.profile.profile_service.ProfileRepository.save",
                side_effect=save,
            ),
        ):
            uploaded = await ProfileService.upload_avatar(_user(), _upload(PNG))
            stored = ProfileImageStorage.relative_from_public_url(uploaded.avatar_url)
            removed = await ProfileService.remove_avatar(_user())
        assert stored is not None
        assert removed.avatar_url is None
        assert not ProfileImageStorage.resolve_path(stored).exists()

    asyncio.run(run())
    get_settings.cache_clear()


def test_upload_rejects_a_file_that_is_not_an_image(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)
    profile = _profile()

    async def run() -> None:
        with patch(
            "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
            new=AsyncMock(return_value=profile),
        ):
            with pytest.raises(AppException) as exc:
                await ProfileService.upload_avatar(
                    _user(),
                    _upload(b"GIF89a", "photo.gif", "image/gif"),
                )
        assert exc.value.code == "INVALID_FILE_TYPE"

    asyncio.run(run())
    get_settings.cache_clear()


def test_delete_owned_url_leaves_an_external_avatar_alone(tmp_path, monkeypatch) -> None:
    _use_storage(tmp_path, monkeypatch)
    ProfileImageStorage.delete_owned_url("https://cdn.example.com/avatar.png", USER_ID)
    get_settings.cache_clear()
