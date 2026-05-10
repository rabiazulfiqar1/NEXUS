"""
Unit tests for app.services.crew.career_crew — mock path and cache behavior.

Skipped entirely if crewai is not installed.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

crewai = pytest.importorskip("crewai", reason="crewai not installed")

from app.services.crew.tasks import GeneratedCV
from tests.conftest import SAMPLE_GENERATED_CV


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  run_career_analysis — mock path
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestRunCareerAnalysisMockPath:
    @pytest.mark.asyncio
    @patch("app.services.crew.career_crew.get_async_client")
    @patch("app.services.crew.career_crew.get_redis")
    @patch("app.services.crew.career_crew.LLM_USE_MOCK", True)
    async def test_mock_mode_returns_generated_cv(self, mock_redis_fn, mock_client_fn):
        from app.services.crew.career_crew import run_career_analysis

        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock()
        mock_redis_fn.return_value = mock_redis

        # Mock Supabase client
        mock_client = AsyncMock()
        chain = MagicMock()
        chain.upsert.return_value = chain
        chain.execute = AsyncMock()
        mock_client.table = MagicMock(return_value=chain)
        mock_client_fn.return_value = mock_client

        cv = await run_career_analysis("user-1", "Backend Engineer")

        assert isinstance(cv, GeneratedCV)
        assert "Backend Engineer" in cv.professional_summary
        assert len(cv.skills) > 0
        assert 0.0 <= cv.ats_score <= 1.0

    @pytest.mark.asyncio
    @patch("app.services.crew.career_crew.get_async_client")
    @patch("app.services.crew.career_crew.get_redis")
    @patch("app.services.crew.career_crew.LLM_USE_MOCK", True)
    async def test_mock_mode_caches_to_redis(self, mock_redis_fn, mock_client_fn):
        from app.services.crew.career_crew import run_career_analysis

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock()
        mock_redis_fn.return_value = mock_redis

        mock_client = AsyncMock()
        chain = MagicMock()
        chain.upsert.return_value = chain
        chain.execute = AsyncMock()
        mock_client.table = MagicMock(return_value=chain)
        mock_client_fn.return_value = mock_client

        await run_career_analysis("user-1", "SWE")

        # Verify Redis setex was called
        mock_redis.setex.assert_called_once()
        cache_key = mock_redis.setex.call_args[0][0]
        assert "career_cv:user-1:swe" == cache_key

    @pytest.mark.asyncio
    @patch("app.services.crew.career_crew.get_async_client")
    @patch("app.services.crew.career_crew.get_redis")
    @patch("app.services.crew.career_crew.LLM_USE_MOCK", True)
    async def test_mock_mode_persists_to_supabase(self, mock_redis_fn, mock_client_fn):
        from app.services.crew.career_crew import run_career_analysis

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock()
        mock_redis_fn.return_value = mock_redis

        mock_client = AsyncMock()
        chain = MagicMock()
        chain.upsert.return_value = chain
        chain.execute = AsyncMock()
        mock_client.table = MagicMock(return_value=chain)
        mock_client_fn.return_value = mock_client

        await run_career_analysis("user-1", "Data Scientist")

        # Verify Supabase upsert was called
        mock_client.table.assert_called_with("career_reports")
        chain.upsert.assert_called_once()
        upsert_data = chain.upsert.call_args[0][0]
        assert upsert_data["user_id"] == "user-1"
        assert upsert_data["target_role"] == "Data Scientist"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  run_career_analysis — cache hit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestRunCareerAnalysisCacheHit:
    @pytest.mark.asyncio
    @patch("app.services.crew.career_crew.get_redis")
    async def test_returns_cached_result(self, mock_redis_fn):
        from app.services.crew.career_crew import run_career_analysis

        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps(SAMPLE_GENERATED_CV))
        mock_redis_fn.return_value = mock_redis

        cv = await run_career_analysis("user-1", "Backend Engineer")

        assert isinstance(cv, GeneratedCV)
        assert cv.professional_summary == SAMPLE_GENERATED_CV["professional_summary"]
        assert cv.ats_score == SAMPLE_GENERATED_CV["ats_score"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GeneratedCV validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGeneratedCVValidation:
    def test_from_dict(self):
        cv = GeneratedCV(**SAMPLE_GENERATED_CV)
        assert cv.ats_score == 0.72
        assert "Python" in cv.skills

    def test_model_dump_roundtrip(self):
        cv = GeneratedCV(**SAMPLE_GENERATED_CV)
        dumped = cv.model_dump()
        cv2 = GeneratedCV(**dumped)
        assert cv == cv2

    def test_json_serialization(self):
        cv = GeneratedCV(**SAMPLE_GENERATED_CV)
        json_str = cv.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["ats_score"] == 0.72
