"""
API endpoint tests for the Users router (/profile/*).
All external dependencies are mocked via conftest fixtures.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from tests.conftest import MockUser, SAMPLE_PROFILE


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST /profile/resume
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestProfileResume:
    def test_no_file_returns_message(self, auth_client):
        response = auth_client.post("/api/v1/profile/resume")
        assert response.status_code == 201
        assert "upload" in response.json()["message"].lower() or "PDF" in response.json()["message"]

    def test_invalid_file_type_returns_400(self, auth_client):
        response = auth_client.post(
            "/api/v1/profile/resume",
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()

    @patch("app.routers.users.extract_text", return_value="Extracted resume text")
    @patch("app.routers.users.add_resume", new_callable=AsyncMock)
    @patch("app.routers.users.add_profile_embedding", new_callable=AsyncMock)
    def test_valid_pdf_upload_succeeds(
        self, mock_embed, mock_add_resume, mock_extract, auth_client
    ):
        response = auth_client.post(
            "/api/v1/profile/resume",
            files={"file": ("resume.pdf", b"%PDF-fake-content", "application/pdf")},
        )
        assert response.status_code == 201
        assert "success" in response.json()["message"].lower()
        mock_extract.assert_called_once()
        mock_add_resume.assert_called_once()
        mock_embed.assert_called_once()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST /profile/manual
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestProfileManual:
    @patch("app.routers.users.add_user_profile", new_callable=AsyncMock)
    @patch("app.routers.users.add_profile_embedding", new_callable=AsyncMock)
    def test_valid_manual_profile(self, mock_embed, mock_add_profile, auth_client):
        payload = {
            "full_name": "Test User",
            "skills": ["Python", "SQL"],
            "degree": "BS CS",
            "graduation_year": 2025,
            "experience": [{"company": "Acme", "role": "Intern"}],
            "projects": [{"name": "NEXUS"}],
        }
        response = auth_client.post("/api/v1/profile/manual", json=payload)
        assert response.status_code == 201
        assert "success" in response.json()["message"].lower()

    @patch("app.routers.users.add_user_profile", new_callable=AsyncMock)
    @patch("app.routers.users.add_profile_embedding", new_callable=AsyncMock)
    def test_minimal_manual_profile(self, mock_embed, mock_add_profile, auth_client):
        response = auth_client.post("/api/v1/profile/manual", json={})
        assert response.status_code == 201


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DELETE /profile/resume
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestDeleteResume:
    def test_delete_resume_succeeds(self, auth_client, mock_supabase_client):
        response = auth_client.delete("/api/v1/profile/resume")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower() or "success" in response.json()["message"].lower()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GET /profile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetProfile:
    def test_get_profile_returns_data(self, auth_client, mock_supabase_client):
        # Configure mock to return profile data
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = SAMPLE_PROFILE
        for m in ("select", "eq", "single"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/profile")
        assert response.status_code == 200

    def test_get_profile_returns_empty_when_missing(self, auth_client, mock_supabase_client):
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = None
        for m in ("select", "eq", "single"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/profile")
        assert response.status_code == 200
        assert response.json() == {}
