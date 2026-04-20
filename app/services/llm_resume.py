import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL, LLM_USE_MOCK


def enhance_resume(resume_text: str, target_role: str) -> dict:
    if LLM_USE_MOCK:
        return {
            "mode": "mock",
            "target_role": target_role,
            "summary": "Entry-level candidate with hands-on backend/API experience and strong learning pace.",
            "improved_bullets": [
                "Built REST APIs with FastAPI and integrated Supabase for storage and retrieval.",
                "Implemented vector embeddings and similarity matching for personalized job recommendations.",
                "Improved data ingestion reliability by handling empty payload edge cases in persistence layer.",
            ],
            "missing_keywords": ["docker", "unit testing", "ci/cd"],
            "next_steps": [
                "Add measurable outcomes for each project bullet.",
                "Group technical skills by backend, databases, and tools.",
            ],
        }

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Set LLM_USE_MOCK=true to run without paid API access.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
You are a resume optimization assistant.
Target role: {target_role}
Resume text:
{resume_text}

Return strict JSON with keys:
- summary (string)
- improved_bullets (array of strings)
- missing_keywords (array of strings)
- next_steps (array of strings)
"""
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    text_output = response.output_text
    parsed = json.loads(text_output)
    parsed["mode"] = "live"
    parsed["target_role"] = target_role
    return parsed


def generate_cv(profile_text: str, target_role: str) -> dict:
    if LLM_USE_MOCK:
        return {
            "mode": "mock",
            "target_role": target_role,
            "professional_summary": "Software engineering student focused on backend systems, APIs, and data-driven products.",
            "skills": ["Python", "FastAPI", "Supabase", "SQL", "Git"],
            "experience_bullets": [
                "Created backend services for user profiles and resume ingestion workflows.",
                "Designed job recommendation flow using semantic embeddings and vector similarity.",
            ],
            "projects": [
                "NEXUS: AI-assisted job matching platform with profile parsing and recommendation APIs."
            ],
        }

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is missing. Set LLM_USE_MOCK=true to run without paid API access.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
You are a CV writer.
Target role: {target_role}
Profile text:
{profile_text}

Return strict JSON with keys:
- professional_summary (string)
- skills (array of strings)
- experience_bullets (array of strings)
- projects (array of strings)
"""
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    text_output = response.output_text
    parsed = json.loads(text_output)
    parsed["mode"] = "live"
    parsed["target_role"] = target_role
    return parsed
