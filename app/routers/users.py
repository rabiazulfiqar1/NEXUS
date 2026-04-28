from fastapi import APIRouter, Depends, File, UploadFile, status
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ALLOWED_FILE_TYPES
from supabase import create_client
from app.core.dependencies import get_current_user
from app.schemas.user import UserCreate
import tempfile
import os
from app.services.resume_parser import extract_text, build_user_embedding_text
from app.db.database import add_resume, add_user_profile, add_profile_embedding, get_user_profile_data

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

router = APIRouter()

@router.post("/profile/resume", status_code=status.HTTP_201_CREATED)
async def create_profile_from_resume(user : dict = Depends(get_current_user), file: UploadFile = File(None)):
    if not file:
        return {"message": "Please upload a PDF file"}
    
    content_type = file.content_type
    if content_type not in ALLOWED_FILE_TYPES:
        return {"error": "File extension not allowed"}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    resume_text = extract_text(tmp_path)
    os.remove(tmp_path)
    add_resume(resume_text, user.id)
    add_profile_embedding(resume_text, user.id)
    return {"message": "Resume uploaded successfully"}
    

@router.post("/profile/manual", status_code=status.HTTP_201_CREATED)
async def create_profile_manual(profile: UserCreate, user: dict = Depends(get_current_user)):
    data = profile.model_dump()
    data["id"] = str(user.id)
    add_user_profile(data)
    profile_text = build_user_embedding_text(data)
    add_profile_embedding(profile_text, user.id)
    return {"message": "User profile created successfully"}

@router.get("/profile")
async def get_my_profile(user: dict = Depends(get_current_user)):
    return get_user_profile_data(user.id)

@router.delete("/profile/resume")
async def delete_my_resume(user: dict = Depends(get_current_user)):
    client.table("user_profiles").update({
        "resume_text": None,
        "embedding": None,
        "is_embed": False
    }).eq("id", str(user.id)).execute()
    return {"message": "Resume deleted successfully"}