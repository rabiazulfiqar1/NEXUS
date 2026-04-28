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
    try:
        return enhance_resume(resume_text=resume_text, target_role=payload.target_role, profile=profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Service Error: {str(e)}"
        )


@router.post("/resume/enhance/test", response_model=ResumeEnhanceResponse)
def enhance_resume_test(payload: ResumeEnhanceRequest):
    # Temporary test endpoint without authentication
    sample_resume_text = """
John Doe
Software Engineer with experience in Python, FastAPI, and React.
Education: Bachelor of Computer Science, 2022
Experience:
- Developed REST APIs using FastAPI
- Built web applications with React
- Worked with PostgreSQL databases
Projects:
- E-commerce platform with React and Node.js
- Data analytics dashboard with Python
"""
    
    sample_profile = {
        "degree": "Bachelor of Computer Science",
        "graduation_year": 2022,
        "experience": [
            {"title": "Software Developer", "company": "Tech Corp", "duration": "1 year"},
            {"title": "Intern", "company": "StartupXYZ", "duration": "3 months"}
        ],
        "projects": [
            {"name": "E-commerce platform", "tech": ["React", "Node.js"]},
            {"name": "Data analytics dashboard", "tech": ["Python", "PostgreSQL"]}
        ]
    }
    
    try:
        return enhance_resume(resume_text=sample_resume_text, target_role=payload.target_role, profile=sample_profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Service Error: {str(e)}"
        )


@router.get("/profile/status")
def get_profile_status(user: dict = Depends(get_current_user)):
    try:
        profile = get_user_profile_data(user.id)
        return {
            "has_profile": True,
            "has_resume_text": bool(profile.get("resume_text")),
            "has_degree": bool(profile.get("degree")),
            "has_graduation_year": bool(profile.get("graduation_year")),
            "has_experience": bool(profile.get("experience")),
            "has_projects": bool(profile.get("projects")),
            "profile_data": {
                "full_name": profile.get("full_name"),
                "degree": profile.get("degree"),
                "graduation_year": profile.get("graduation_year"),
                "experience_count": len(profile.get("experience", [])),
                "projects_count": len(profile.get("projects", [])),
                "skills_count": len(profile.get("skills", [])),
                "has_resume_text": bool(profile.get("resume_text"))
            }
        }
    except HTTPException as e:
        if e.status_code == 404:
            return {
                "has_profile": False,
                "message": "No profile found. Please upload a resume first.",
                "user_id": user.id,
                "user_email": user.email
            }
        raise e


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
