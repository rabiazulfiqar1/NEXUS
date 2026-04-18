from supabase import create_client
from app.schemas.job import JobCreate
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from app.services.embedding import generate_embedding
client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def add_jobs(job_list: list[JobCreate]):
    jobs = [job.model_dump() for job in job_list]
    for job in jobs:
        if job.get("posted_at"):
            job["posted_at"] = job["posted_at"].isoformat()
    client.table("job_listings").upsert(jobs, on_conflict="url").execute()

def embed_jobs(job_list: list[JobCreate]):
    for job in job_list:
        text = f"{job.description} {job.title}"
        embedding = generate_embedding(text)
        client.table("job_listings")\
            .update({"embedding": embedding})\
            .eq("url", job.url)\
            .execute()
        
# client.table("job_listings").select("id, title, description").is_("embedding", "null").execute()