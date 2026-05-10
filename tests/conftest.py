"""
Shared test fixtures for the NEXUS test suite.

All external dependencies (Supabase, Redis, LLM providers) are mocked
so that the full suite runs offline without any API keys or services.

IMPORTANT: Environment variables are set BEFORE any app module is imported
to prevent Supabase/config crashes at import time.
"""
import os
import sys
from pathlib import Path

# ── Set dummy env vars BEFORE any app import ──────────────────────────────────
# Several modules (config.py, resume_parser.py, dependencies.py) create
# Supabase clients at module-level. They crash if these env vars are missing.

_TEST_ENV = {
    "NEXT_PUBLIC_SUPABASE_URL": os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "https://test.supabase.co"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-key"),
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", ""),
    "GROQ_MODEL": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    "LLM_PROVIDER": os.environ.get("LLM_PROVIDER", "mock"),
    "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", ""),
    "JOB_SEARCH_API": os.environ.get("JOB_SEARCH_API", "test-api-key"),
    "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY", "test-tavily-key"),
}
for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now safe to import test utilities
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest


# ── Mock user ─────────────────────────────────────────────────────────────────

class MockUser:
    """Lightweight stand-in for a Supabase auth user object."""
    def __init__(self, id: str = "test-user-00000000-0000-0000-0000-000000000001",
                 email: str = "testuser@nexus.dev"):
        self.id = id
        self.email = email


@pytest.fixture
def mock_user():
    return MockUser()


# ── Mock Supabase async client ────────────────────────────────────────────────

def _build_mock_table_chain(return_data=None):
    """
    Build a fluent mock that mirrors Supabase's chained query API:
        client.table("x").select("y").eq("k","v").execute()
    """
    chain = MagicMock()
    execute_result = MagicMock()
    execute_result.data = return_data if return_data is not None else []

    for method in ("select", "insert", "upsert", "update", "delete",
                   "eq", "order", "limit", "single"):
        getattr(chain, method).return_value = chain

    chain.execute = AsyncMock(return_value=execute_result)
    return chain


@pytest.fixture
def mock_supabase_client():
    """Returns an AsyncMock that behaves like a Supabase AsyncClient."""
    client = AsyncMock()
    client.table = MagicMock(side_effect=lambda _name: _build_mock_table_chain())
    client.rpc = MagicMock(side_effect=lambda _fn, _params: _build_mock_table_chain())
    client.auth = AsyncMock()
    return client


# ── Mock Redis ────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock()
    redis.zremrangebyscore = AsyncMock()
    redis.zadd = AsyncMock()
    redis.zcard = AsyncMock(return_value=0)
    redis.expire = AsyncMock()
    redis.zrange = AsyncMock(return_value=[])

    # Pipeline context manager
    pipe = AsyncMock()
    pipe.zremrangebyscore = AsyncMock()
    pipe.zadd = AsyncMock()
    pipe.zcard = AsyncMock()
    pipe.expire = AsyncMock()
    pipe.execute = AsyncMock(return_value=[None, None, 1, None])

    pipe_cm = AsyncMock()
    pipe_cm.__aenter__ = AsyncMock(return_value=pipe)
    pipe_cm.__aexit__ = AsyncMock(return_value=False)
    redis.pipeline = MagicMock(return_value=pipe_cm)

    return redis


# ── Test client with auth override ───────────────────────────────────────────

def _has_crewai():
    """Check if crewai is importable (needed for app.main)."""
    try:
        import crewai  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.fixture
def auth_client(mock_supabase_client, mock_redis):
    """
    FastAPI TestClient with:
      - get_current_user → returns MockUser
      - get_async_client → returns mock supabase client
      - get_redis → returns mock redis

    Skipped if crewai is not installed (required by app.main imports).
    """
    if not _has_crewai():
        pytest.skip("crewai not installed — cannot create FastAPI TestClient")

    from app.main import app
    from app.core.dependencies import get_current_user
    from app.db.async_client import get_async_client
    from app.core.redis_client import get_redis
    from fastapi.testclient import TestClient

    user = MockUser()

    async def _override_user():
        return user

    async def _override_client():
        return mock_supabase_client

    async def _override_redis():
        return mock_redis

    async def _override_get_client():
        return mock_supabase_client

    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[get_async_client] = _override_client
    app.dependency_overrides[get_redis] = _override_redis

    # Patch the database module's _get_client and resume_parser's get_user_profile_data
    with patch("app.db.database._get_client", new_callable=lambda: AsyncMock(return_value=mock_supabase_client)):
        with patch("app.routers.resume_tools.get_user_profile_data", new_callable=lambda: AsyncMock(return_value={
            "id": "test-user",
            "resume_text": "Test resume",
            "skills": ["Python", "FastAPI"],
        })):
            with TestClient(app, raise_server_exceptions=False) as client:
                yield client

    app.dependency_overrides.clear()


# ── Sample data factories ────────────────────────────────────────────────────

SAMPLE_PROFILE = {
    "id": "test-user-00000000-0000-0000-0000-000000000001",
    "full_name": "Test User",
    "github_url": "https://github.com/testuser",
    "linkedin_url": "https://linkedin.com/in/testuser",
    "resume_text": "Experienced Python developer with 3 years of FastAPI experience.",
    "skills": ["Python", "FastAPI", "SQL", "Docker"],
    "degree": "BS Computer Science",
    "graduation_year": 2025,
    "experience": [{"company": "Acme Corp", "role": "Backend Intern", "duration": "6 months"}],
    "projects": [{"name": "NEXUS", "description": "AI career platform"}],
    "experience_years": 2,
}

SAMPLE_JOB = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "title": "Backend Engineer",
    "company": "TechCorp",
    "location": "Remote",
    "description": "Looking for Python, FastAPI, Docker expertise.",
    "employment_type": "FULLTIME",
    "source": "LinkedIn",
    "url": "https://example.com/jobs/1",
    "posted_at": "2026-01-15T00:00:00",
    "similarity": 0.85,
}

SAMPLE_GENERATED_CV = {
    "professional_summary": "Backend engineer with Python and FastAPI expertise.",
    "skills": ["Python", "FastAPI", "SQL"],
    "experience_bullets": ["Built REST APIs", "Optimised database queries"],
    "projects": ["NEXUS: AI career platform"],
    "ats_score": 0.72,
    "trending_skills_used": ["Python", "FastAPI"],
    "skill_gaps_remaining": ["Kubernetes", "AWS"],
}
