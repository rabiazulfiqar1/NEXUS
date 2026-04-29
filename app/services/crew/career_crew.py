from crewai import Crew, Process
from app.services.crew.tasks import build_tasks, GeneratedCV
from app.core.redis_client import get_redis
from app.db.async_client import get_async_client
from app.core.config import LLM_USE_MOCK
import json

CACHE_TTL = 3600  # 1 hour

async def run_career_analysis(user_id: str, target_role: str) -> GeneratedCV:
    redis  = await get_redis()
    cache_key = f"career_cv:{user_id}:{target_role.lower().replace(' ', '_')}"

    # ── Cache check ───────────────────────────────────────────────────────────
    try:
        cached = await redis.get(cache_key)
        if cached:
            return GeneratedCV(**json.loads(cached))
    except Exception:
        pass

    # ── Mock path (fast) ─────────────────────────────────────────────────────
    if LLM_USE_MOCK:
        cv = GeneratedCV(
            professional_summary=(
                f"Mock analysis for {target_role}: focused on core strengths, "
                "relevant experience, and clear impact."
            ),
            skills=["Python", "SQL", "Data Analysis", "FastAPI"],
            experience_bullets=[
                "Built data pipelines and APIs to support analytics workflows.",
                "Improved reporting reliability and reduced manual effort.",
                "Collaborated with cross-functional teams on data-driven projects.",
            ],
            projects=["Portfolio dashboard", "ATS resume optimizer"],
            ats_score=0.62,
            trending_skills_used=["Python", "SQL"],
            skill_gaps_remaining=["Cloud", "ML Ops"],
        )
        try:
            await redis.setex(cache_key, CACHE_TTL, json.dumps(cv.model_dump()))
        except Exception:
            pass
        client = await get_async_client()
        await client.table("career_reports").upsert({
            "user_id":     user_id,
            "target_role": target_role,
            "report":      cv.model_dump(),
        }, on_conflict="user_id,target_role").execute()
        return cv

    # ── Build crew ────────────────────────────────────────────────────────────
    tasks  = build_tasks(user_id, target_role)
    agents = list({id(t.agent): t.agent for t in tasks}.values())

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=True,
        embedder={
            "provider": "sentence-transformer",
            "config": {
                "model": "all-MiniLM-L6-v2",
            }
        },
    )

    # ── Run ───────────────────────────────────────────────────────────────────
    result = crew.kickoff()
    cv: GeneratedCV = result.pydantic

    # ── Cache result ──────────────────────────────────────────────────────────
    try:
        await redis.setex(cache_key, CACHE_TTL, json.dumps(cv.model_dump()))
    except Exception:
        pass

    # ── Persist to Supabase ───────────────────────────────────────────────────
    client = await get_async_client()
    await client.table("career_reports").upsert({
        "user_id":     user_id,
        "target_role": target_role,
        "report":      cv.model_dump(),
    }, on_conflict="user_id,target_role").execute()

    return cv