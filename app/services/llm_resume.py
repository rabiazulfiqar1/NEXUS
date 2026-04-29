import json
import re
import requests
from fastapi import HTTPException, status
from openai import OpenAI
from groq import Groq
from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    # LLM_USE_MOCK,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)


def _mock_enhance_response(target_role: str) -> dict:
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


def _mock_cv_response(target_role: str) -> dict:
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


def _coerce_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _fallback_projects(target_role: str) -> list[str]:
    role = target_role.strip() or "Software Engineer"
    return [
        f"{role} Portfolio Project: Build and deploy an end-to-end app with clear impact metrics.",
        f"{role} API Project: Design a production-ready REST API with auth, tests, and documentation.",
        f"{role} Data Project: Create a role-relevant analytics/dashboard workflow and publish results.",
    ]


def _is_low_quality_project(project: str) -> bool:
    text = project.strip().lower()
    if len(text) < 18:
        return True
    weak_markers = [
        "xyz",
        "project 1",
        "project x",
        "internship",
        "sample project",
        "dummy",
    ]
    return any(marker in text for marker in weak_markers)


def _normalize_cv_payload(payload: dict, target_role: str) -> dict:
    payload["skills"] = _coerce_str_list(payload.get("skills"))
    payload["experience_bullets"] = _coerce_str_list(payload.get("experience_bullets"))
    projects = _coerce_str_list(payload.get("projects"))
    good_projects = [project for project in projects if not _is_low_quality_project(project)]
    payload["projects"] = good_projects if good_projects else _fallback_projects(target_role)
    if not isinstance(payload.get("professional_summary"), str) or not payload.get("professional_summary", "").strip():
        payload["professional_summary"] = (
            f"Candidate preparing for {target_role} roles with practical project and backend experience."
        )
    return payload


def _extract_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned an invalid response format.",
            )
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned malformed JSON.",
            ) from exc


def _call_openai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is missing.",
        )
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(model=OPENAI_MODEL, input=prompt)
        return response.output_text or ""
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI request failed.",
        ) from exc


def _call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama request failed. Make sure Ollama is running and model is pulled.",
        ) from exc


def _call_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENROUTER_API_KEY is missing.",
        )
    try:
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content or ""
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenRouter request failed.",
        ) from exc


def _call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GROQ_API_KEY is missing.",
        )
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content or ""
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq request failed: {str(exc)}",
        ) from exc


def _call_llm(prompt: str) -> tuple[str, str]:
    # use_mock = LLM_USE_MOCK or LLM_PROVIDER == "mock"
    # if use_mock:
    #     return "mock", ""
    # if LLM_PROVIDER == "openai":
    #     return "openai", _call_openai(prompt)
    # if LLM_PROVIDER == "ollama":
    #     return "ollama", _call_ollama(prompt)
    if LLM_PROVIDER == "groq":
        try:
            return "groq", _call_groq(prompt)
        except HTTPException:
            return "openrouter", _call_openrouter(prompt)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Invalid LLM_PROVIDER. Use one of: mock, ollama, openai, groq.",
    )


def enhance_resume(resume_text: str, target_role: str, profile: dict = None) -> dict:
    # Extract user data from profile
    user_info = ""
    if profile:
        degree = profile.get("degree", "")
        graduation_year = profile.get("graduation_year", "")
        experience = profile.get("experience", [])
        projects = profile.get("projects", [])
        
        user_info = f"""
User Profile Data:
- Degree: {degree}
- Graduation Year: {graduation_year}
- Experience: {experience}
- Projects: {projects}
"""
    
    prompt = f"""
You are a resume optimization assistant for the target role: {target_role}

{user_info}

Original Resume Text:
{resume_text}

Instructions:
1. Use the user's actual degree, graduation year, experience, and projects from the profile data
2. Enhance the resume specifically for the {target_role} role
3. Change any "CORE COMPETENCIES & SKILLS" sections to just "SKILLS"
4. Provide improved bullet points that highlight relevant achievements
5. Identify missing keywords that are important for {target_role} roles
6. Suggest specific next steps to strengthen the resume

Return strict JSON with keys:
- summary (string) - Professional summary optimized for {target_role}
- improved_bullets (array of strings) - Enhanced bullet points using user's actual experience
- missing_keywords (array of strings) - Key skills missing for {target_role}
- next_steps (array of strings) - Actionable improvement suggestions
"""
    mode, llm_text = _call_llm(prompt)
    if mode == "mock":
        return _mock_enhance_response(target_role)

    parsed = _extract_json_object(llm_text)
    parsed["mode"] = mode
    parsed["target_role"] = target_role
    return parsed


def generate_cv(profile_text: str, target_role: str) -> dict:
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

Rules:
- Use ONLY information grounded in the profile text.
- Do NOT invent company names, internships, or project titles.
- If project details are missing, return an empty projects array.
"""
    mode, llm_text = _call_llm(prompt)
    if mode == "mock":
        return _mock_cv_response(target_role)

    parsed = _extract_json_object(llm_text)
    parsed = _normalize_cv_payload(parsed, target_role)
    parsed["mode"] = mode
    parsed["target_role"] = target_role
    return parsed
