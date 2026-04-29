from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
from app.core.config import TAVILY_API_KEY
from app.db.database import get_user_profile_data, get_jobs
from app.services.resume_parser import ats_score, build_user_embedding_text
from app.services.llm_resume import enhance_resume
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

def _run_async(coro):
    """Always run in a fresh event loop to avoid FastAPI loop conflicts."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Tool schemas ──────────────────────────────────────────────────────────────

class UserIdInput(BaseModel):
    user_id: str = Field(description="The user's UUID")

class ATSInput(BaseModel):
    user_id: str = Field(description="The user's UUID")
    job_id:  str = Field(description="The job listing UUID")

class EnhanceInput(BaseModel):
    resume_text: str = Field(description="Raw resume or profile text")
    target_role: str = Field(description="Target job role")

class MarketInput(BaseModel):
    target_role: str = Field(description="Target job role to research")


# ── Tools ─────────────────────────────────────────────────────────────────────

class FetchProfileTool(BaseTool):
    name: str = "fetch_user_profile"
    description: str = (
        "Fetches the user's resume text, skills, degree, experience, projects, "
        "and profile metadata from the database."
    )
    args_schema: type[BaseModel] = UserIdInput

    def _run(self, user_id: str) -> dict:
        data = _run_async(get_user_profile_data(user_id))
        data.pop("profile_text", None)
        return data


class FetchMatchedJobsTool(BaseTool):
    name: str = "fetch_matched_jobs"
    description: str = "Fetches top semantically matched job listings for the user."
    args_schema: type[BaseModel] = UserIdInput

    def _run(self, user_id: str) -> list[dict]:
        jobs = _run_async(get_jobs(user_id))
        for job in jobs:
            if "id" not in job and "job_id" in job:
                job["id"] = str(job["job_id"])
            elif "id" in job and job["id"] is not None:
                job["id"] = str(job["id"])
        return jobs


# class ATSScoreTool(BaseTool):
#     name: str = "compute_ats_score"
#     description: str = "Computes ATS match score (0.0-1.0) between user profile and a specific job."
#     args_schema: type[BaseModel] = ATSInput

#     def _run(self, user_id: str, job_id: str) -> float:
#         return _run_async(ats_score(user_id, job_id))

class ATSBatchScoreTool(BaseTool):
    name: str = "compute_ats_scores_batch"
    description: str = (
        "Computes ATS match scores for multiple jobs at once. "
        "Always prefer this over compute_ats_score when scoring more than one job."
    )

    class InputSchema(BaseModel):
        user_id: str = Field(description="The user's UUID")
        job_ids: list[str] = Field(description="List of job UUIDs to score")

    args_schema: type[BaseModel] = InputSchema

    def _run(self, user_id: str, job_ids: list[str]) -> dict[str, float]:
        def _is_placeholder(job_id: str) -> bool:
            return job_id.lower().startswith("id") and job_id[2:].isdigit()

        if not job_ids or any(_is_placeholder(jid) for jid in job_ids):
            jobs = _run_async(get_jobs(user_id))
            normalized_ids = []
            for job in jobs:
                job_id = job.get("id") or job.get("job_id")
                if job_id:
                    normalized_ids.append(str(job_id))
            job_ids = normalized_ids[: max(len(job_ids), 3)] if normalized_ids else []
        if not job_ids:
            return {}

        def _score(job_id):
            return job_id, _run_async(ats_score(user_id, job_id))

        results = {}
        with ThreadPoolExecutor(max_workers=len(job_ids)) as executor:
            futures = {executor.submit(_score, jid): jid for jid in job_ids}
            for future in as_completed(futures):
                job_id, score = future.result()
                results[job_id] = score
        return results


class EnhanceResumeTool(BaseTool):
    name: str = "enhance_resume"
    description: str = (
        "Rewrites resume bullets using trending keywords, "
        "identifies missing keywords, and suggests next steps."
    )
    args_schema: type[BaseModel] = EnhanceInput

    def _run(self, resume_text: str, target_role: str) -> dict:
        from app.services.llm_resume import enhance_resume as _enhance
        return _enhance(resume_text=resume_text, target_role=target_role)


class MarketResearchTool(BaseTool):
    name: str = "market_research"
    description: str = (
        "Searches the web for current in-demand skills and trends "
        "for a given job role. Returns a synthesized summary + sources."
    )
    args_schema: type[BaseModel] = MarketInput

    def _run(self, target_role: str) -> str:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=f"{target_role} required skills trends 2025 job market",
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )
        answer  = response.get("answer", "No summary available.")
        sources = [
            f"- {r['title']}: {r['content'][:300]}"
            for r in response.get("results", [])
        ]
        return f"Summary:\n{answer}\n\nSources:\n" + "\n".join(sources)