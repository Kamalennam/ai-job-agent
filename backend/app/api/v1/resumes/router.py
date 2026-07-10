from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeDetailResponse, ResumeListResponse, ResumeResponse
from app.services.resume.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    return await ResumeService.upload(current_user.id, file, is_primary=is_primary)


@router.get("", response_model=ResumeListResponse)
async def list_resumes(current_user: User = Depends(get_current_user)) -> ResumeListResponse:
    return await ResumeService.list_resumes(current_user.id)


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
) -> ResumeDetailResponse:
    return await ResumeService.get_resume(current_user.id, resume_id)
