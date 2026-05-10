"""
API endpoint tests for the Resume Tools router (/resume/*, /cv/*).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST /resume/enhance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestResumeEnhance:
    @patch("app.routers.resume_tools.enhance_resume")
    @patch("app.routers.resume_tools.get_user_profile_data", new_callable=AsyncMock)
    def test_valid_enhance_request(self, mock_profile, mock_enhance, auth_client):
        mock_profile.return_value = {
            "resume_text": "Python developer with FastAPI experience.",
            "skills": ["Python", "FastAPI"],
        }
        mock_enhance.return_value = {
            "mode": "groq",
            "target_role": "Backend Engineer",
            "summary": "Strong backend developer.",
            "improved_bullets": ["Built scalable APIs"],
            "missing_keywords": ["Docker"],
            "next_steps": ["Add CI/CD experience"],
        }
        response = auth_client.post(
            "/api/v1/resume/enhance",
            json={"target_role": "Backend Engineer"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "groq"
        assert data["target_role"] == "Backend Engineer"
        assert "summary" in data
        assert isinstance(data["improved_bullets"], list)

    @patch("app.routers.resume_tools.get_user_profile_data", new_callable=AsyncMock)
    def test_no_profile_data_returns_400(self, mock_profile, auth_client):
        mock_profile.return_value = {"resume_text": None, "skills": []}
        response = auth_client.post(
            "/api/v1/resume/enhance",
            json={"target_role": "Backend Engineer"},
        )
        assert response.status_code == 400
        assert "No usable profile" in response.json()["detail"]

    def test_target_role_too_short_returns_422(self, auth_client):
        response = auth_client.post(
            "/api/v1/resume/enhance",
            json={"target_role": "A"},
        )
        assert response.status_code == 422

    def test_missing_target_role_returns_422(self, auth_client):
        response = auth_client.post("/api/v1/resume/enhance", json={})
        assert response.status_code == 422


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST /cv/generate
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCVGenerate:
    @patch("app.routers.resume_tools.generate_cv")
    @patch("app.routers.resume_tools.get_user_profile_data", new_callable=AsyncMock)
    def test_valid_cv_generate(self, mock_profile, mock_cv, auth_client):
        mock_profile.return_value = {
            "resume_text": "Python developer",
            "skills": ["Python"],
        }
        mock_cv.return_value = {
            "mode": "groq",
            "target_role": "SWE",
            "professional_summary": "Talented developer.",
            "skills": ["Python", "FastAPI"],
            "experience_bullets": ["Built REST APIs"],
            "projects": ["NEXUS"],
        }
        response = auth_client.post(
            "/api/v1/cv/generate",
            json={"target_role": "SWE"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "groq"
        assert isinstance(data["skills"], list)

    @patch("app.routers.resume_tools.get_user_profile_data", new_callable=AsyncMock)
    def test_no_profile_data_returns_400(self, mock_profile, auth_client):
        mock_profile.return_value = {"resume_text": "", "skills": []}
        response = auth_client.post(
            "/api/v1/cv/generate",
            json={"target_role": "Backend Engineer"},
        )
        assert response.status_code == 400

    def test_missing_target_role_returns_422(self, auth_client):
        response = auth_client.post("/api/v1/cv/generate", json={})
        assert response.status_code == 422

    @patch("app.routers.resume_tools.generate_cv")
    @patch("app.routers.resume_tools.get_user_profile_data", new_callable=AsyncMock)
    def test_llm_error_returns_500(self, mock_profile, mock_cv, auth_client):
        mock_profile.return_value = {"resume_text": "Some text", "skills": ["Python"]}
        mock_cv.side_effect = Exception("LLM timeout")
        response = auth_client.post(
            "/api/v1/cv/generate",
            json={"target_role": "Backend Eng"},
        )
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
