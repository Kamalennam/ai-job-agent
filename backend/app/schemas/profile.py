from pydantic import BaseModel, EmailStr, Field, field_validator


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _http_url(value: str | None) -> str | None:
    cleaned = _blank_to_none(value)
    if cleaned is None:
        return None
    if not cleaned.startswith(("http://", "https://")):
        raise ValueError("Enter a full http or https URL")
    return cleaned


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=160)
    location: str | None = Field(default=None, max_length=120)
    linkedin_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=2000)

    @field_validator("full_name")
    @classmethod
    def name_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Full name is required")
        return cleaned

    @field_validator("headline", "location", "bio")
    @classmethod
    def optional_text(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @field_validator("linkedin_url")
    @classmethod
    def optional_url(cls, value: str | None) -> str | None:
        return _http_url(value)


class ProfileResponse(BaseModel):
    id: str
    email: EmailStr
    email_verified: bool
    full_name: str
    headline: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
