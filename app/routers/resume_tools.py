from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.db.database import get_user_profile_data
from app.schemas.llm_resume import (
    ResumeEnhanceRequest,
    ResumeEnhanceResponse,
    CVGenerateRequest,
    CVGenerateResponse,
)
from app.services.llm_resume import enhance_resume, generate_cv
from app.services.resume_parser import build_user_embedding_text


router = APIRouter()


def _build_profile_text(profile: dict) -> str:
    resume_text = (profile.get("resume_text") or "").strip()
    if resume_text:
        return resume_text
    return build_user_embedding_text(profile)


@router.post("/resume/enhance", response_model=ResumeEnhanceResponse)
def enhance_user_resume(payload: ResumeEnhanceRequest, user: dict = Depends(get_current_user)):
    profile = get_user_profile_data(user.id)
    resume_text = _build_profile_text(profile)
    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No usable profile data found. Upload a resume or complete manual profile first.",
        )
    return enhance_resume(resume_text=resume_text, target_role=payload.target_role)


@router.post("/cv/generate", response_model=CVGenerateResponse)
def generate_user_cv(payload: CVGenerateRequest, user: dict = Depends(get_current_user)):
    profile = get_user_profile_data(user.id)
    profile_text = _build_profile_text(profile)
    if not profile_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No usable profile data found. Upload a resume or complete manual profile first.",
        )
    return generate_cv(profile_text=profile_text, target_role=payload.target_role)
