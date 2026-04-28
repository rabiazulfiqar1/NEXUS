from app.services import llm_resume


def test_generate_cv_uses_fallback_projects_when_missing(monkeypatch):
    def fake_call_llm(_prompt: str):
        return "ollama", "{}"

    def fake_extract_json(_text: str):
        return {
            "professional_summary": "Backend-focused student",
            "skills": ["Python", "FastAPI"],
            "experience_bullets": ["Built REST APIs"],
            "projects": [],
        }

    monkeypatch.setattr(llm_resume, "_call_llm", fake_call_llm)
    monkeypatch.setattr(llm_resume, "_extract_json_object", fake_extract_json)

    result = llm_resume.generate_cv("profile text", "Backend Intern")

    assert result["mode"] == "ollama"
    assert result["target_role"] == "Backend Intern"
    assert isinstance(result["projects"], list)
    assert len(result["projects"]) == 3
    assert all(isinstance(project, str) and project for project in result["projects"])


def test_generate_cv_replaces_low_quality_projects(monkeypatch):
    def fake_call_llm(_prompt: str):
        return "openai", "{}"

    def fake_extract_json(_text: str):
        return {
            "professional_summary": "Backend-focused student",
            "skills": ["Python"],
            "experience_bullets": ["Built APIs"],
            "projects": ["XYZ Corp Backend Internship", "Project 1"],
        }

    monkeypatch.setattr(llm_resume, "_call_llm", fake_call_llm)
    monkeypatch.setattr(llm_resume, "_extract_json_object", fake_extract_json)

    result = llm_resume.generate_cv("profile text", "Backend Intern")

    assert result["mode"] == "openai"
    assert len(result["projects"]) == 3
    assert all("xyz" not in project.lower() for project in result["projects"])
    assert all("project 1" not in project.lower() for project in result["projects"])


def test_generate_cv_preserves_valid_projects(monkeypatch):
    valid_projects = [
        "Built a job recommendation API using FastAPI, pgvector, and Supabase with 90%+ relevance.",
        "Deployed a resume parsing pipeline with PDF extraction, validation, and profile enrichment.",
    ]

    def fake_call_llm(_prompt: str):
        return "openai", "{}"

    def fake_extract_json(_text: str):
        return {
            "professional_summary": "Backend-focused student",
            "skills": ["Python", "SQL"],
            "experience_bullets": ["Built APIs", "Optimized queries"],
            "projects": valid_projects,
        }

    monkeypatch.setattr(llm_resume, "_call_llm", fake_call_llm)
    monkeypatch.setattr(llm_resume, "_extract_json_object", fake_extract_json)

    result = llm_resume.generate_cv("profile text", "Backend Intern")

    assert result["mode"] == "openai"
    assert result["projects"] == valid_projects
