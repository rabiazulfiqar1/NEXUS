from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ALLOWED_FILE_TYPES
from supabase import create_client
from app.core.dependencies import get_current_user
from app.schemas.user import UserCreate
import tempfile
import os
from app.services.resume_parser import extract_text, build_user_embedding_text
from app.db.database import add_resume, add_user_profile, add_profile_embedding
import asyncio

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

router = APIRouter()

@router.post("/profile/resume", status_code=201)
async def create_profile_from_resume(
    user: dict = Depends(get_current_user),
    file: UploadFile = File(None)
):
    if not file:
        return {"message": "Please upload a PDF file"}
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File extension not allowed")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    resume_text = await asyncio.get_event_loop().run_in_executor(
        None, extract_text, tmp_path        # pdfplumber is blocking
    )
    os.remove(tmp_path)

    # both DB writes can run concurrently
    await asyncio.gather(
        add_resume(resume_text, user.id),
        add_profile_embedding(resume_text, user.id),
    )
    return {"message": "Resume uploaded successfully"}
    

@router.post("/profile/manual", status_code=201)
async def create_profile_manual(
    profile: UserCreate,
    user: dict = Depends(get_current_user)
):
    data = profile.model_dump()
    data["id"] = user.id
    profile_text = build_user_embedding_text(data)
    await asyncio.gather(
        add_user_profile(data),
        add_profile_embedding(profile_text, user.id),
    )
    return {"message": "User profile created successfully"}
