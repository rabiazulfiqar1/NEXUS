from supabase import create_client
from app.schemas.job import JobCreate
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, MATCH_COUNT, MATCH_THRESHOLD
from app.services.embedding import generate_embedding
from fastapi import HTTPException, status

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def add_jobs(job_list: list[JobCreate]):
    if not job_list:
        return
    jobs = [job.model_dump() for job in job_list]
    for job in jobs:
        if job.get("posted_at"):
            job["posted_at"] = job["posted_at"].isoformat()
    client.table("job_listings").upsert(jobs, on_conflict="url").execute()

def embed_jobs(job_list: list[JobCreate]):
    if not job_list:
        return
    for job in job_list:
        text = f"{job.description} {job.title}"
        embedding = generate_embedding(text)
        client.table("job_listings")\
            .update({"embedding": embedding})\
            .eq("url", job.url)\
            .execute()
        
def add_resume(resume_text: str, user_id):
    client.table("user_profiles").upsert({
        "id": str(user_id),
        "resume_text": resume_text
    }).execute()

def add_user_profile(user_profile: dict):
    client.table("user_profiles").upsert(user_profile).execute()

def add_profile_embedding(text:str, user_id):
    embedding = generate_embedding(text)
    client.table("user_profiles").update({"embedding": embedding, "is_embed": True}).eq("id", str(user_id)).execute()

def get_jobs(user_id):
    result = client.table("user_profiles").select("embedding").eq("id", str(user_id)).execute()
    if not result.data or not result.data[0]["embedding"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile or embedding not found"
        )
    embedding = result.data[0]["embedding"]
    jobs = client.rpc("get_similar_jobs", {
        "user_embedding": embedding,
        "match_threshold": MATCH_THRESHOLD,
        "match_count": MATCH_COUNT
    }).execute()
    if not jobs.data:
        return []
    return jobs.data

def get_user_profile_data(user_id) -> dict:
    # First try to get all columns to see what exists
    try:
        result = client.table("user_profiles").select("*").eq("id", str(user_id)).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return result.data[0]
    except Exception as e:
        # If that fails, try minimal columns
        result = client.table("user_profiles").select("id").eq("id", str(user_id)).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return result.data[0]