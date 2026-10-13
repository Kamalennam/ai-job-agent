from fastapi import APIRouter, Depends, File, UploadFile

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.profile import ProfileResponse, UpdateProfileRequest
from app.services.profile.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)) -> ProfileResponse:
    return await ProfileService.get(current_user)


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    return await ProfileService.update(current_user, payload)


@router.post("/me/avatar", response_model=ProfileResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    return await ProfileService.upload_avatar(current_user, file)


@router.delete("/me/avatar", response_model=ProfileResponse)
async def remove_avatar(current_user: User = Depends(get_current_user)) -> ProfileResponse:
    return await ProfileService.remove_avatar(current_user)
