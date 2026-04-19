from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.db.database import get_jobs

router = APIRouter()

@router.get("/jobs")
def get_user_similarity_jobs(user: dict = Depends(get_current_user)):
    return get_jobs(user.id)