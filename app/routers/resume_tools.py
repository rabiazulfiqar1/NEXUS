from fastapi import APIRouter, Depends, HTTPException, Request
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
import asyncio
import inspect
from app.core.rate_limiter import rate_limit

router = APIRouter()


def _build_profile_text(profile: dict) -> str:
    resume_text = (profile.get("resume_text") or "").strip()
    if resume_text:
        return resume_text
    return build_user_embedding_text(profile)


@router.post("/resume/enhance", response_model=ResumeEnhanceResponse)
async def enhance_user_resume(
    request: Request,
    payload: ResumeEnhanceRequest,
    user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit("resume_enhance")),
):
    try:
        profile = get_user_profile_data(user.id)
        if inspect.isawaitable(profile):
            profile = await profile
        resume_text = _build_profile_text(profile)
        if not resume_text:
            raise HTTPException(status_code=400, detail="No usable profile data found.")
        # LLM calls are blocking — offload to thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None, enhance_resume, resume_text, payload.target_role
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in enhance_user_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/cv/generate", response_model=CVGenerateResponse)
async def generate_user_cv(
    request: Request,
    payload: CVGenerateRequest,
    user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit("cv_generate")),
):
    try:
        profile = get_user_profile_data(user.id)
        if inspect.isawaitable(profile):
            profile = await profile
        profile_text = _build_profile_text(profile)
        if not profile_text:
            raise HTTPException(status_code=400, detail="No usable profile data found.")
        result = await asyncio.get_event_loop().run_in_executor(
            None, generate_cv, profile_text, payload.target_role
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_user_cv: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")