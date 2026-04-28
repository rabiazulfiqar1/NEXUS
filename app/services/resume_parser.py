import pdfplumber
from app.core.config import GROK_API_KEY
from groq import Groq
from app.db.database import get_similarity_score
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from supabase import create_client
import json
from fastapi import HTTPException

supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

groq_client = Groq(GROK_API_KEY)

def extract_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            # print(page.extract_text())

    return text

def build_user_embedding_text(profile: dict) -> str:
    skills_text = " ".join(profile.get("skills") or [])
    degree_text = profile.get("degree") or ""
    experience_text = ""
    for exp in profile.get("experience") or []:
        for key, val in exp.items():
            experience_text += f"{key}: {val} "
    
    return f"{skills_text} {degree_text} {experience_text}".strip()


def extract_skills_with_llm(text: str) -> list[str]:
    SYSTEM_PROMPT = """Your job is to parse text and extract Skills
    Example: Input: Skills: REST API, FastAPI, React
    Output: ['REST API', 'FastAPI', 'React']
    OUTPUT FORMAT: [parsed_skills_array]
    """

    response = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            },
        ],
        model="qwen/qwen3-32b"
    )

    return json.loads(response.choices[0].message.content)

def ats_score(user_id, job_id):
    sim_score = get_similarity_score(user_id, job_id)
    user_response = supabase_client.table("user_profiles").select("resume_text", "skills").eq("id", user_id).execute()
    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")
    if user_response.data[0]["resume_text"]:
        user_skills = extract_skills_with_llm(user_response.data[0]["resume_text"])
    else:
        user_skills = user_response.data[0]["skills"]
    user_skills = set([s.lower() for s in user_skills])

    job_response = supabase_client.table("job_listings").select("description").eq("id", job_id).execute()
    if job_response.data[0]["description"]:
        reqs = extract_skills_with_llm(job_response.data[0]["description"])
        reqs = set([r.lower() for r in reqs])
    else:
        return sim_score
    
    intersection = user_skills & reqs
    skill_score = len(intersection) / len(reqs) if reqs else 0
    return 0.6*sim_score + 0.4*skill_score

    
