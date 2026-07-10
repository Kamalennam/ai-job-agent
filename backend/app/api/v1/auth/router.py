from fastapi import APIRouter, Depends, Request

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(payload: RegisterRequest) -> RegisterResponse:
    result = await AuthService.register(payload)
    return RegisterResponse(**result)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest) -> MessageResponse:
    result = await AuthService.verify_email(payload.token)
    return MessageResponse(**result)


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email_query(token: str) -> MessageResponse:
    result = await AuthService.verify_email(token)
    return MessageResponse(**result)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(payload: ResendVerificationRequest) -> MessageResponse:
    result = await AuthService.resend_verification(payload.email)
    return MessageResponse(**result)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request) -> TokenResponse:
    return await AuthService.login(
        payload.email,
        payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    return await AuthService.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)) -> MessageResponse:
    result = await AuthService.logout(current_user.id)
    return MessageResponse(**result)
