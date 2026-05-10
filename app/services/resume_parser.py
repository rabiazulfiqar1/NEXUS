import json
import pdfplumber
from fastapi import HTTPException
from groq import Groq
from openai import OpenAI
import inspect
from app.core.config import (
    GROQ_API_KEY,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)
from app.db.database import get_similarity_score
from supabase import create_client

supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def extract_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            # print(page.extract_text())

    return text

def build_user_embedding_text(profile: dict) -> str:
    resume_text = (profile.get("resume_text") or "").strip()
    if resume_text:
        return resume_text
    skills_text = " ".join(profile.get("skills") or [])
    degree_text = profile.get("degree") or ""
    experience_text = ""
    for exp in profile.get("experience") or []:
        for key, val in exp.items():
            experience_text += f"{key}: {val} "
    projects_text = ""
    for proj in profile.get("projects") or []:
        for key, val in proj.items():
            projects_text += f"{key}: {val} "
    experience_years = profile.get("experience_years")
    experience_years_text = f"Experience Years: {experience_years} " if experience_years else ""

    return f"{skills_text} {degree_text} {experience_text} {projects_text} {experience_years_text}".strip()


def extract_skills_with_llm(text: str) -> list[str]:
    # SYSTEM_PROMPT = """Your job is to parse text and extract Skills
    # Example: Input: Skills: REST API, FastAPI, React
    # Output: ['REST API', 'FastAPI', 'React']
    # OUTPUT FORMAT: [parsed_skills_array]
    # """

    # try:
    #     if GROQ_API_KEY:
    #         groq_client = Groq(api_key=GROQ_API_KEY)
    #         response = groq_client.chat.completions.create(
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": SYSTEM_PROMPT,
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": text,
    #                 },
    #             ],
    #             model="qwen/qwen3-32b",
    #         )
    #         return json.loads(response.choices[0].message.content)
    # except Exception:
    #     pass

    # if not OPENROUTER_API_KEY:
    #     raise HTTPException(status_code=502, detail="OpenRouter fallback is not configured")

    # try:
    #     openrouter_client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
    #     response = openrouter_client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": SYSTEM_PROMPT,
    #             },
    #             {
    #                 "role": "user",
    #                 "content": text,
    #             },
    #         ],
    #         model=OPENROUTER_MODEL,
    #     )
    #     return json.loads(response.choices[0].message.content)
    # except json.JSONDecodeError as exc:
    #     raise HTTPException(status_code=502, detail="LLM returned invalid JSON for skills") from exc
    # except Exception as exc:
    #     raise HTTPException(status_code=502, detail="OpenRouter request failed") from exc
    mock_skills = ['REST API', 'FastAPI', 'React', 'Python', 'Docker']

    return [skill for skill in mock_skills if skill.lower() in text.lower()] or mock_skills[:3]


async def _resolve(value):
    if inspect.isawaitable(value):
        return await value
    return value

async def ats_score(user_id: str, job_id: str) -> float:
    sim_score = await get_similarity_score(user_id, job_id)

    user_response = await _resolve(supabase_client.table("user_profiles") \
        .select("resume_text", "skills") \
        .eq("id", user_id) \
        .execute())
    
    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_response.data[0]
    if user_data["skills"]:
        user_skills = user_data["skills"] or []
    else:
        user_skills = extract_skills_with_llm(user_data["resume_text"])
    user_skills = set(s.lower() for s in user_skills)

    job_response = await _resolve(supabase_client.table("job_listings") \
        .select("description") \
        .eq("id", job_id) \
        .execute())
    
    if not job_response.data or not job_response.data[0]["description"]:
        return sim_score
    
    reqs = set(r.lower() for r in extract_skills_with_llm(job_response.data[0]["description"]))
    
    skill_score = len(user_skills & reqs) / len(reqs) if reqs else 0.0
    return round(0.6 * sim_score + 0.4 * skill_score, 4)