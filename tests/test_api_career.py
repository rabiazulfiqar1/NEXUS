"""
API endpoint tests for the Career router (/career/*).

Skipped entirely if crewai is not installed since the career router
imports from the crew module at module level.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

crewai = pytest.importorskip("crewai", reason="crewai not installed")

from tests.conftest import SAMPLE_GENERATED_CV


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POST /career/analyze
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCareerAnalyze:
    def test_empty_target_role_returns_400(self, auth_client):
        response = auth_client.post(
            "/api/v1/career/analyze",
            params={"target_role": "   "},
        )
        assert response.status_code == 400
        assert "target_role" in response.json()["detail"].lower()

    @patch("app.routers.career.run_career_analysis", new_callable=AsyncMock)
    def test_valid_analysis_returns_cv(self, mock_analyze, auth_client):
        from app.services.crew.tasks import GeneratedCV
        mock_analyze.return_value = GeneratedCV(**SAMPLE_GENERATED_CV)

        response = auth_client.post(
            "/api/v1/career/analyze",
            params={"target_role": "Backend Engineer"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "professional_summary" in data
        assert "ats_score" in data
        assert isinstance(data["skills"], list)

    @patch("app.routers.career.run_career_analysis", new_callable=AsyncMock)
    def test_analysis_failure_returns_500(self, mock_analyze, auth_client):
        mock_analyze.side_effect = Exception("Crew crashed")
        response = auth_client.post(
            "/api/v1/career/analyze",
            params={"target_role": "Data Scientist"},
        )
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GET /career/cv/latest
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCareerCVLatest:
    def test_no_cv_returns_404(self, auth_client, mock_supabase_client):
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = []
        for m in ("select", "eq", "order", "limit"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/career/cv/latest")
        assert response.status_code == 404

    def test_returns_latest_cv(self, auth_client, mock_supabase_client):
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = [{
            "report": SAMPLE_GENERATED_CV,
            "target_role": "Backend Engineer",
            "created_at": "2026-01-01T00:00:00",
        }]
        for m in ("select", "eq", "order", "limit"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/career/cv/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["professional_summary"] == SAMPLE_GENERATED_CV["professional_summary"]
        assert data["ats_score"] == 0.72


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GET /career/cv/export
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCareerCVExport:
    def test_no_cv_returns_404(self, auth_client, mock_supabase_client):
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = []
        for m in ("select", "eq", "order", "limit"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/career/cv/export")
        assert response.status_code == 404

    @patch("app.routers.career.export_cv_to_pdf", return_value=b"%PDF-1.4 fake content")
    def test_exports_pdf(self, mock_export, auth_client, mock_supabase_client):
        chain = MagicMock()
        execute_result = MagicMock()
        execute_result.data = [{"report": SAMPLE_GENERATED_CV}]
        for m in ("select", "eq", "order", "limit"):
            getattr(chain, m).return_value = chain
        chain.execute = AsyncMock(return_value=execute_result)
        mock_supabase_client.table = MagicMock(return_value=chain)

        response = auth_client.get("/api/v1/career/cv/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert b"%PDF" in response.content
