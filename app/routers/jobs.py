from fastapi import APIRouter, Depends, Request
from app.core.dependencies import get_current_user
from app.db.database import get_jobs
from uuid import UUID
from app.services.resume_parser import ats_score
from app.core.rate_limiter import rate_limit

router = APIRouter()

@router.get("/jobs")
async def get_user_similarity_jobs(user: dict = Depends(get_current_user)):
    return await get_jobs(user.id)

@router.get("/jobs/{job_id}/ats-score")
async def get_ats_score(
    request: Request,
    job_id: UUID, 
    user: dict = Depends(get_current_user),
    _: None = Depends(rate_limit("ats_score")),
):
    result = await ats_score(user.id, job_id)
    return {"job_id": str(job_id), "ats_score": result}