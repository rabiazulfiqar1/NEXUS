"""
Unit tests for app.services.job_fetcher — HTTP fetch, deduplication, and error handling.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  fetch_jobs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOCK_API_RESPONSE = {
    "data": [
        {
            "job_title": "Backend Engineer",
            "employer_name": "TechCorp",
            "job_location": "Remote",
            "job_employment_type": "FULLTIME",
            "job_publisher": "LinkedIn",
            "job_description": "Python FastAPI expertise needed.",
            "job_apply_link": "https://example.com/jobs/1",
            "job_posted_at_timestamp": 1704067200,  # 2024-01-01
        },
        {
            "job_title": "Data Scientist",
            "employer_name": "DataCo",
            "job_location": "Karachi",
            "job_employment_type": "INTERN",
            "job_publisher": "Indeed",
            "job_description": "ML and Python skills required.",
            "job_apply_link": "https://example.com/jobs/2",
            "job_posted_at_timestamp": None,
        },
    ]
}


class TestFetchJobs:
    @pytest.mark.asyncio
    async def test_fetches_and_stores_jobs(self, monkeypatch):
        from app.services import job_fetcher

        # Mock aiohttp session
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=MOCK_API_RESPONSE)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock(return_value=False)

        import aiohttp
        monkeypatch.setattr(aiohttp, "ClientSession", lambda: mock_session_cm)

        # Mock DB operations
        mock_add_jobs = AsyncMock()
        mock_embed_jobs = AsyncMock()
        monkeypatch.setattr(job_fetcher, "add_jobs", mock_add_jobs)
        monkeypatch.setattr(job_fetcher, "embed_jobs", mock_embed_jobs)

        # Limit to 1 query for testing speed
        monkeypatch.setattr(job_fetcher, "CRON_QUERIES", ["test query"])

        await job_fetcher.fetch_jobs()

        mock_add_jobs.assert_called_once()
        mock_embed_jobs.assert_called_once()

        # Verify job_list passed to add_jobs
        added_jobs = mock_add_jobs.call_args[0][0]
        assert len(added_jobs) == 2
        assert added_jobs[0].title == "Backend Engineer"
        assert added_jobs[1].title == "Data Scientist"

    @pytest.mark.asyncio
    async def test_deduplicates_by_url(self, monkeypatch):
        from app.services import job_fetcher

        duplicate_response = {
            "data": [
                {
                    "job_title": "Engineer",
                    "employer_name": "Corp",
                    "job_description": "desc",
                    "job_apply_link": "https://same-url.com",
                    "job_posted_at_timestamp": None,
                },
                {
                    "job_title": "Engineer v2",
                    "employer_name": "Corp",
                    "job_description": "desc2",
                    "job_apply_link": "https://same-url.com",  # same URL
                    "job_posted_at_timestamp": None,
                },
            ]
        }

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=duplicate_response)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock(return_value=False)

        import aiohttp
        monkeypatch.setattr(aiohttp, "ClientSession", lambda: mock_session_cm)

        mock_add_jobs = AsyncMock()
        mock_embed_jobs = AsyncMock()
        monkeypatch.setattr(job_fetcher, "add_jobs", mock_add_jobs)
        monkeypatch.setattr(job_fetcher, "embed_jobs", mock_embed_jobs)
        monkeypatch.setattr(job_fetcher, "CRON_QUERIES", ["test"])

        await job_fetcher.fetch_jobs()

        added_jobs = mock_add_jobs.call_args[0][0]
        assert len(added_jobs) == 1  # deduplicated

    @pytest.mark.asyncio
    async def test_handles_api_error_gracefully(self, monkeypatch):
        from app.services import job_fetcher

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(
            side_effect=Exception("API Error")
        )

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=False),
        ))

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_cm.__aexit__ = AsyncMock(return_value=False)

        import aiohttp
        monkeypatch.setattr(aiohttp, "ClientSession", lambda: mock_session_cm)

        mock_add_jobs = AsyncMock()
        mock_embed_jobs = AsyncMock()
        monkeypatch.setattr(job_fetcher, "add_jobs", mock_add_jobs)
        monkeypatch.setattr(job_fetcher, "embed_jobs", mock_embed_jobs)
        monkeypatch.setattr(job_fetcher, "CRON_QUERIES", ["failing query"])

        # Should not raise — errors are caught per query
        await job_fetcher.fetch_jobs()

        # Empty list passed since all queries failed
        mock_add_jobs.assert_called_once()
        added_jobs = mock_add_jobs.call_args[0][0]
        assert len(added_jobs) == 0
