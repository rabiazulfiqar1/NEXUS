"""
Unit tests for app.services.llm_resume — JSON extraction, normalization,
mock responses, and the public enhance_resume / generate_cv functions.
"""
import pytest
from fastapi import HTTPException
from app.services import llm_resume


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _extract_json_object
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestExtractJsonObject:
    def test_valid_json(self):
        result = llm_resume._extract_json_object('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_embedded_in_markdown(self):
        text = '```json\n{"summary": "Good"}\n```'
        result = llm_resume._extract_json_object(text)
        assert result["summary"] == "Good"

    def test_json_with_surrounding_text(self):
        text = 'Here is the result:\n{"a": 1, "b": 2}\nDone.'
        result = llm_resume._extract_json_object(text)
        assert result == {"a": 1, "b": 2}

    def test_garbage_input_raises_http_exception(self):
        with pytest.raises(HTTPException) as exc_info:
            llm_resume._extract_json_object("no json here at all")
        assert exc_info.value.status_code == 502

    def test_malformed_json_raises_http_exception(self):
        with pytest.raises(HTTPException) as exc_info:
            llm_resume._extract_json_object("{broken: json,}")
        assert exc_info.value.status_code == 502

    def test_empty_string_raises_http_exception(self):
        with pytest.raises(HTTPException):
            llm_resume._extract_json_object("")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _coerce_str_list
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCoerceStrList:
    def test_valid_list(self):
        assert llm_resume._coerce_str_list(["Python", "SQL"]) == ["Python", "SQL"]

    def test_list_with_empty_strings(self):
        assert llm_resume._coerce_str_list(["Python", "", "SQL"]) == ["Python", "SQL"]

    def test_non_list_returns_empty(self):
        assert llm_resume._coerce_str_list("not a list") == []

    def test_none_returns_empty(self):
        assert llm_resume._coerce_str_list(None) == []

    def test_list_with_numbers_coerces_to_str(self):
        assert llm_resume._coerce_str_list([1, 2, 3]) == ["1", "2", "3"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _is_low_quality_project
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestIsLowQualityProject:
    def test_too_short(self):
        assert llm_resume._is_low_quality_project("Short") is True

    def test_xyz_marker(self):
        assert llm_resume._is_low_quality_project("XYZ Corp Backend Internship") is True

    def test_project_1_marker(self):
        assert llm_resume._is_low_quality_project("Project 1: Simple CRUD app") is True

    def test_sample_project_marker(self):
        assert llm_resume._is_low_quality_project("This is a sample project for learning") is True

    def test_dummy_marker(self):
        assert llm_resume._is_low_quality_project("A dummy placeholder project entry here") is True

    def test_valid_project(self):
        valid = "Built a job recommendation API using FastAPI, pgvector, and Supabase with 90%+ relevance."
        assert llm_resume._is_low_quality_project(valid) is False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _fallback_projects
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestFallbackProjects:
    def test_returns_three_projects(self):
        result = llm_resume._fallback_projects("Backend Engineer")
        assert len(result) == 3

    def test_projects_contain_target_role(self):
        result = llm_resume._fallback_projects("Data Scientist")
        assert all("Data Scientist" in p for p in result)

    def test_empty_role_defaults(self):
        result = llm_resume._fallback_projects("")
        assert all("Software Engineer" in p for p in result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _normalize_cv_payload
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestNormalizeCVPayload:
    def test_missing_summary_gets_fallback(self):
        payload = {"professional_summary": "", "skills": [], "experience_bullets": [], "projects": []}
        result = llm_resume._normalize_cv_payload(payload, "SWE")
        assert "SWE" in result["professional_summary"]

    def test_none_summary_gets_fallback(self):
        payload = {"professional_summary": None, "skills": [], "experience_bullets": [], "projects": []}
        result = llm_resume._normalize_cv_payload(payload, "SWE")
        assert result["professional_summary"] != ""

    def test_empty_projects_get_fallback(self):
        payload = {"professional_summary": "Good", "skills": ["Python"], "experience_bullets": ["Built APIs"], "projects": []}
        result = llm_resume._normalize_cv_payload(payload, "Backend")
        assert len(result["projects"]) == 3

    def test_valid_data_preserved(self):
        payload = {
            "professional_summary": "Strong engineer",
            "skills": ["Python", "SQL"],
            "experience_bullets": ["Led team"],
            "projects": ["Built a production-grade ML pipeline with end-to-end monitoring."],
        }
        result = llm_resume._normalize_cv_payload(payload, "ML Eng")
        assert result["professional_summary"] == "Strong engineer"
        assert result["projects"] == ["Built a production-grade ML pipeline with end-to-end monitoring."]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Mock responses
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestMockResponses:
    def test_mock_enhance_response_structure(self):
        result = llm_resume._mock_enhance_response("Backend Engineer")
        assert result["mode"] == "mock"
        assert result["target_role"] == "Backend Engineer"
        assert isinstance(result["summary"], str)
        assert isinstance(result["improved_bullets"], list)
        assert isinstance(result["missing_keywords"], list)
        assert isinstance(result["next_steps"], list)

    def test_mock_cv_response_structure(self):
        result = llm_resume._mock_cv_response("Frontend Dev")
        assert result["mode"] == "mock"
        assert result["target_role"] == "Frontend Dev"
        assert isinstance(result["professional_summary"], str)
        assert isinstance(result["skills"], list)
        assert isinstance(result["experience_bullets"], list)
        assert isinstance(result["projects"], list)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  enhance_resume (mocked LLM)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestEnhanceResume:
    def test_returns_expected_structure(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("groq", "{}"))
        monkeypatch.setattr(llm_resume, "_extract_json_object", lambda _t: {
            "summary": "Strong Python developer",
            "improved_bullets": ["Built scalable APIs"],
            "missing_keywords": ["Docker"],
            "next_steps": ["Add CI/CD experience"],
        })
        result = llm_resume.enhance_resume("resume text here", "Backend Engineer")
        assert result["mode"] == "groq"
        assert result["target_role"] == "Backend Engineer"
        assert result["summary"] == "Strong Python developer"

    def test_mock_mode_returns_mock_response(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("mock", ""))
        result = llm_resume.enhance_resume("resume", "DevOps")
        assert result["mode"] == "mock"
        assert result["target_role"] == "DevOps"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  generate_cv (mocked LLM) — existing tests + new ones
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGenerateCV:
    def test_uses_fallback_projects_when_missing(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("ollama", "{}"))
        monkeypatch.setattr(llm_resume, "_extract_json_object", lambda _t: {
            "professional_summary": "Backend-focused student",
            "skills": ["Python", "FastAPI"],
            "experience_bullets": ["Built REST APIs"],
            "projects": [],
        })
        result = llm_resume.generate_cv("profile text", "Backend Intern")
        assert result["mode"] == "ollama"
        assert result["target_role"] == "Backend Intern"
        assert isinstance(result["projects"], list)
        assert len(result["projects"]) == 3
        assert all(isinstance(p, str) and p for p in result["projects"])

    def test_replaces_low_quality_projects(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("openai", "{}"))
        monkeypatch.setattr(llm_resume, "_extract_json_object", lambda _t: {
            "professional_summary": "Backend-focused student",
            "skills": ["Python"],
            "experience_bullets": ["Built APIs"],
            "projects": ["XYZ Corp Backend Internship", "Project 1"],
        })
        result = llm_resume.generate_cv("profile text", "Backend Intern")
        assert result["mode"] == "openai"
        assert len(result["projects"]) == 3
        assert all("xyz" not in p.lower() for p in result["projects"])
        assert all("project 1" not in p.lower() for p in result["projects"])

    def test_preserves_valid_projects(self, monkeypatch):
        valid_projects = [
            "Built a job recommendation API using FastAPI, pgvector, and Supabase with 90%+ relevance.",
            "Deployed a resume parsing pipeline with PDF extraction, validation, and profile enrichment.",
        ]
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("openai", "{}"))
        monkeypatch.setattr(llm_resume, "_extract_json_object", lambda _t: {
            "professional_summary": "Backend-focused student",
            "skills": ["Python", "SQL"],
            "experience_bullets": ["Built APIs", "Optimized queries"],
            "projects": valid_projects,
        })
        result = llm_resume.generate_cv("profile text", "Backend Intern")
        assert result["mode"] == "openai"
        assert result["projects"] == valid_projects

    def test_mock_mode_returns_mock_response(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("mock", ""))
        result = llm_resume.generate_cv("profile", "SWE")
        assert result["mode"] == "mock"
        assert "professional_summary" in result

    def test_normalized_output_has_all_keys(self, monkeypatch):
        monkeypatch.setattr(llm_resume, "_call_llm", lambda _p: ("groq", "{}"))
        monkeypatch.setattr(llm_resume, "_extract_json_object", lambda _t: {
            "professional_summary": "Solid engineer",
            "skills": "not a list",  # intentionally wrong type
            "experience_bullets": ["Built services"],
            "projects": ["A very valid project description that is long enough to pass the filter."],
        })
        result = llm_resume.generate_cv("text", "Backend Eng")
        assert isinstance(result["skills"], list)
        assert result["skills"] == []  # coerced from string
        assert result["mode"] == "groq"
        assert result["target_role"] == "Backend Eng"
