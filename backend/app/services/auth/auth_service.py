from datetime import timedelta

from beanie import PydanticObjectId

from app.config import get_settings
from app.core.exceptions import AppException
from app.core.jwt import create_access_token
from app.core.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.profile import Profile
from app.models.session import Session
from app.models.settings import UserSettings
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.email.email_service import send_verification_email
from app.utils.datetime_utils import ensure_utc, utc_now


class AuthService:
    @staticmethod
    async def register(data: RegisterRequest) -> dict[str, str]:
        email = data.email.lower()
        existing = await UserRepository.get_by_email(email)
        if existing:
            raise AppException(409, "DUPLICATE_EMAIL", "An account with this email already exists")

        verification_token = generate_token()
        settings = get_settings()
        expires_at = utc_now() + timedelta(hours=settings.email_verification_expire_hours)

        user = User(
            email=email,
            password_hash=hash_password(data.password),
            verification_token_hash=hash_token(verification_token),
            verification_token_expires_at=expires_at,
        )
        user = await UserRepository.create(user)

        await ProfileRepository.create(
            Profile(user_id=user.id, full_name=data.full_name.strip())
        )
        await SettingsRepository.create(UserSettings(user_id=user.id))

        verification_url = f"{settings.frontend_base_url}/verify-email?token={verification_token}"
        await send_verification_email(email, verification_url)

        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "email": email,
        }

    @staticmethod
    async def verify_email(token: str) -> dict[str, str]:
        token_hash = hash_token(token)
        user = await UserRepository.get_by_verification_token_hash(token_hash)
        if not user:
            raise AppException(400, "INVALID_TOKEN", "Invalid or expired verification token")

        if user.email_verified:
            return {"message": "Email is already verified. You can sign in."}

        if (
            user.verification_token_expires_at is None
            or ensure_utc(user.verification_token_expires_at) < utc_now()
        ):
            raise AppException(400, "INVALID_TOKEN", "Verification token has expired")

        user.email_verified = True
        await UserRepository.save(user)

        return {"message": "Email verified successfully. You can now sign in."}

    @staticmethod
    async def resend_verification(email: str) -> dict[str, str]:
        user = await UserRepository.get_by_email(email.lower())
        if not user:
            return {"message": "If an account exists, a verification email has been sent."}

        if user.email_verified:
            return {"message": "This email is already verified. You can sign in."}

        settings = get_settings()
        verification_token = generate_token()
        user.verification_token_hash = hash_token(verification_token)
        user.verification_token_expires_at = utc_now() + timedelta(
            hours=settings.email_verification_expire_hours
        )
        await UserRepository.save(user)

        verification_url = f"{settings.frontend_base_url}/verify-email?token={verification_token}"
        await send_verification_email(user.email, verification_url)

        return {"message": "If an account exists, a verification email has been sent."}

    @staticmethod
    async def login(
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        user = await UserRepository.get_by_email(email.lower())
        if not user or not verify_password(password, user.password_hash):
            raise AppException(401, "UNAUTHORIZED", "Invalid email or password")

        if not user.email_verified:
            raise AppException(
                403,
                "EMAIL_NOT_VERIFIED",
                "Please verify your email before signing in.",
            )

        if not user.is_active:
            raise AppException(403, "FORBIDDEN", "Account is disabled")

        return await AuthService._issue_tokens(user, user_agent, ip_address)

    @staticmethod
    async def refresh(refresh_token: str) -> TokenResponse:
        session = await SessionRepository.get_by_refresh_hash(hash_token(refresh_token))
        if not session:
            raise AppException(401, "UNAUTHORIZED", "Invalid refresh token")

        if ensure_utc(session.expires_at) < utc_now():
            await SessionRepository.revoke(session)
            raise AppException(401, "TOKEN_EXPIRED", "Refresh token has expired")

        user = await UserRepository.get_by_id(session.user_id)
        if not user or not user.is_active:
            raise AppException(401, "UNAUTHORIZED", "User account is inactive")

        await SessionRepository.revoke(session)
        return await AuthService._issue_tokens(
            user,
            session.user_agent,
            session.ip_address,
        )

    @staticmethod
    async def logout(user_id: PydanticObjectId) -> dict[str, str]:
        await SessionRepository.revoke_all_for_user(user_id)
        return {"message": "Logged out successfully"}

    @staticmethod
    async def _issue_tokens(
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        settings = get_settings()
        access_token = create_access_token(str(user.id))
        refresh_token = generate_token()
        expires_at = utc_now() + timedelta(days=settings.jwt_refresh_token_expire_days)

        await SessionRepository.create(
            Session(
                user_id=user.id,
                refresh_token_hash=hash_token(refresh_token),
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at,
            )
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )
