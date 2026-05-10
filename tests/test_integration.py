"""
Integration tests for the NEXUS API.

Requires crewai to be installed (app.main imports crew modules).
"""
import pytest
import os

crewai = pytest.importorskip("crewai", reason="crewai not installed")

from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_current_user
from app.db import database
from app.routers import resume_tools


class MockUser:
    def __init__(self, id):
        self.id = id

def override_get_current_user():
    return MockUser(id="test-user-id")

def mock_get_user_profile_data(user_id):
    return {
        "resume_text": "Experienced Python developer with 3 years of FastAPI experience.",
        "skills": ["Python", "FastAPI"],
        "id": user_id
    }


app.dependency_overrides[get_current_user] = override_get_current_user
resume_tools.get_user_profile_data = mock_get_user_profile_data

def test_api_health():
    """Basic check to ensure app runs."""
    client = TestClient(app)
    response = client.get("/")
    # Assuming there's a root endpoint or just checking if it doesn't 404/500
    assert response.status_code in [200, 404]

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_groq_enhance_resume_live(auth_client, monkeypatch):
    """
    Live integration test for Groq Resume Enhancement.
    Requires GROQ_API_KEY and LLM_PROVIDER=groq in environment.
    """
    # Force provider to groq for this test if key is present
    monkeypatch.setattr("app.services.llm_resume.LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.services.llm_resume.LLM_USE_MOCK", False)
    
    payload = {
        "resume_text": "Experienced Python developer with 3 years of FastAPI and SQL experience.",
        "target_role": "Senior Backend Engineer"
    }
    
    response = auth_client.post("/api/v1/resume/enhance", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "groq"
    assert "improved_bullets" in data
    assert "summary" in data

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_groq_generate_cv_live(auth_client, monkeypatch):
    """
    Live integration test for Groq CV Generation.
    Requires GROQ_API_KEY and LLM_PROVIDER=groq in environment.
    """
    monkeypatch.setattr("app.services.llm_resume.LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.services.llm_resume.LLM_USE_MOCK", False)
    
    payload = {
        "target_role": "Backend Intern"
    }
    
    response = auth_client.post("/api/v1/cv/generate", json=payload)
    assert response.status_code == 200

def test_mock_mode_fallback(auth_client, monkeypatch):
    """Verify that setting mock mode works as expected."""
    monkeypatch.setattr("app.services.llm_resume.LLM_USE_MOCK", True)
    
    payload = {
        "resume_text": "Some text",
        "target_role": "DevOps"
    }
    
    response = auth_client.post("/api/v1/resume/enhance", json=payload)
    assert response.status_code == 200
    assert response.json()["mode"] == "mock"
