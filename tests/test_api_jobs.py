"""
API endpoint tests for the Jobs router (/jobs/*).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GET /jobs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetJobs:
    @patch("app.routers.jobs.get_jobs", new_callable=AsyncMock)
    def test_returns_job_list(self, mock_get_jobs, auth_client):
        mock_get_jobs.return_value = [
            {"id": "job-1", "title": "Backend Engineer", "similarity": 0.85},
            {"id": "job-2", "title": "Frontend Dev", "similarity": 0.72},
        ]
        response = auth_client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == "Backend Engineer"

    @patch("app.routers.jobs.get_jobs", new_callable=AsyncMock)
    def test_returns_empty_list(self, mock_get_jobs, auth_client):
        mock_get_jobs.return_value = []
        response = auth_client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.jobs.get_jobs", new_callable=AsyncMock)
    def test_no_embedding_returns_404(self, mock_get_jobs, auth_client):
        mock_get_jobs.side_effect = HTTPException(
            status_code=404,
            detail="User profile or embedding not found",
        )
        response = auth_client.get("/api/v1/jobs")
        assert response.status_code == 404


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GET /jobs/{job_id}/ats-score
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetAtsScore:
    @patch("app.routers.jobs.ats_score")
    def test_returns_ats_score(self, mock_ats, auth_client):
        mock_ats.return_value = 0.78
        job_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        response = auth_client.get(f"/api/v1/jobs/{job_id}/ats-score")
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["ats_score"] == 0.78

    def test_invalid_uuid_returns_422(self, auth_client):
        response = auth_client.get("/api/v1/jobs/not-a-uuid/ats-score")
        assert response.status_code == 422
