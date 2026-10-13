import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from app.core.exceptions import AppException
from app.schemas.profile import UpdateProfileRequest
from app.services.profile.profile_service import ProfileService


def _user() -> SimpleNamespace:
    return SimpleNamespace(id="user-1", email="person@example.com", email_verified=True)


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


def test_get_profile_returns_account_name() -> None:
    profile = _profile(full_name="Kamal")

    async def run() -> None:
        with patch(
            "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
            new=AsyncMock(return_value=profile),
        ):
            result = await ProfileService.get(_user())
        assert result.full_name == "Kamal"
        assert result.email == "person@example.com"

    asyncio.run(run())


def test_update_profile_saves_account_fields() -> None:
    profile = _profile()
    saved: list[object] = []

    async def save(item):
        saved.append(item)
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
            result = await ProfileService.update(
                _user(),
                UpdateProfileRequest(
                    full_name="  Kamal N  ",
                    headline="  ",
                    location="Chennai",
                    linkedin_url="https://www.linkedin.com/in/example",
                    bio=None,
                ),
            )
        assert result.full_name == "Kamal N"
        assert result.headline is None
        assert result.location == "Chennai"
        assert result.avatar_url is None
        assert saved

    asyncio.run(run())


def test_update_profile_requires_a_name() -> None:
    with pytest.raises(ValidationError):
        UpdateProfileRequest(full_name="   ")


def test_update_profile_rejects_a_url_without_a_scheme() -> None:
    with pytest.raises(ValidationError):
        UpdateProfileRequest(full_name="Kamal", linkedin_url="linkedin.com/in/example")


def test_update_profile_keeps_the_uploaded_photo() -> None:
    photo = "https://jobs.example.com/storage/profile-images/user/photo.jpg"
    profile = _profile(avatar_url=photo)

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
            result = await ProfileService.update(
                _user(),
                UpdateProfileRequest(full_name="Kamal"),
            )
        assert result.avatar_url == photo

    asyncio.run(run())


def test_get_profile_reports_missing_profile() -> None:
    async def run() -> None:
        with patch(
            "app.services.profile.profile_service.ProfileRepository.get_by_user_id",
            new=AsyncMock(return_value=None),
        ):
            with pytest.raises(AppException) as exc:
                await ProfileService.get(_user())
        assert exc.value.status_code == 404

    asyncio.run(run())
