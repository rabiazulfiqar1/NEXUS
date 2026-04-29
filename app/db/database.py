from supabase._async.client import AsyncClient
from app.db.async_client import get_async_client
from app.schemas.job import JobCreate
from app.services.embedding import generate_embedding
from app.core.config import MATCH_COUNT, MATCH_THRESHOLD
from fastapi import HTTPException, status
import asyncio

async def _get_client() -> AsyncClient:
    return await get_async_client()

# ── Jobs ──────────────────────────────────────────────────────────────────────

async def add_jobs(job_list: list[JobCreate]) -> None:
    if not job_list:
        return
    client = await _get_client()
    jobs = [job.model_dump() for job in job_list]
    for job in jobs:
        if job.get("posted_at"):
            job["posted_at"] = job["posted_at"].isoformat()
    await client.table("job_listings").upsert(jobs, on_conflict="url").execute()


async def _embed_single_job(client: AsyncClient, job: JobCreate) -> None:
    text = f"{job.description} {job.title}"
    # generate_embedding is a blocking call — run in thread pool
    embedding = await asyncio.get_event_loop().run_in_executor(
        None, generate_embedding, text
    )
    await client.table("job_listings") \
        .update({"embedding": embedding}) \
        .eq("url", job.url) \
        .execute()


async def embed_jobs(job_list: list[JobCreate]) -> None:
    if not job_list:
        return
    client = await _get_client()
    await asyncio.gather(*[_embed_single_job(client, job) for job in job_list])

# ── User profiles ─────────────────────────────────────────────────────────────

async def add_resume(resume_text: str, user_id: str) -> None:
    client = await _get_client()
    await client.table("user_profiles").upsert({
        "id": user_id,
        "resume_text": resume_text,
    }).execute()


async def add_user_profile(user_profile: dict) -> None:
    client = await _get_client()

    user_profile.pop("email", None)

    await client.table("user_profiles") \
        .upsert(user_profile, on_conflict="id") \
        .execute()


async def add_profile_embedding(text: str, user_id: str) -> None:
    embedding = await asyncio.get_event_loop().run_in_executor(
        None, generate_embedding, text
    )
    client = await _get_client()
    await client.table("user_profiles") \
        .update({"embedding": embedding, "is_embed": True}) \
        .eq("id", user_id) \
        .execute()


async def get_jobs(user_id: str) -> list[dict]:
    client = await _get_client()
    result = await client.table("user_profiles") \
        .select("embedding") \
        .eq("id", user_id) \
        .execute()
    if not result.data or not result.data[0]["embedding"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile or embedding not found",
        )
    embedding = result.data[0]["embedding"]
    jobs = await client.rpc("get_similar_jobs", {
        "user_embedding": embedding,
        "match_threshold": MATCH_THRESHOLD,
        "match_count": MATCH_COUNT,
    }).execute()
    return jobs.data or []


async def get_similarity_score(user_id: str, job_id) -> float:
    client = await _get_client()
    response = await client.table("user_profiles") \
        .select("embedding") \
        .eq("id", user_id) \
        .execute()
    user_embedding = response.data[0]["embedding"]
    result = await client.rpc("get_similarity_score", {
        "user_embedding": user_embedding,
        "job_id": str(job_id),
    }).execute()
    if result.data:
        score = result.data
        return float(score[0]) if isinstance(score, list) else float(score)
    return 0.0


async def get_user_profile_data(user_id: str) -> dict:
    client = await _get_client()
    result = await client.table("user_profiles") \
        .select(
            "id, full_name, github_url, linkedin_url, resume_text, skills, degree, "
            "graduation_year, experience, projects, experience_years"
        ) \
        .eq("id", user_id) \
        .execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    return result.data[0]
