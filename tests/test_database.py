"""
Unit tests for app.db.database — all database operations with mocked Supabase client.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _mock_client(return_data=None):
    """Create a mock async Supabase client with fluent chain support."""
    client = AsyncMock()
    chain = MagicMock()
    execute_result = MagicMock()
    execute_result.data = return_data if return_data is not None else []

    for method in ("select", "insert", "upsert", "update", "delete",
                   "eq", "order", "limit", "single"):
        getattr(chain, method).return_value = chain

    chain.execute = AsyncMock(return_value=execute_result)
    client.table = MagicMock(return_value=chain)
    client.rpc = MagicMock(return_value=chain)
    return client, chain, execute_result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  add_jobs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAddJobs:
    @pytest.mark.asyncio
    async def test_empty_list_returns_early(self, monkeypatch):
        from app.db import database
        mock_client, _, _ = _mock_client()
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        await database.add_jobs([])
        mock_client.table.assert_not_called()

    @pytest.mark.asyncio
    async def test_upserts_job_list(self, monkeypatch):
        from app.db import database
        from app.schemas.job import JobCreate

        mock_client, chain, _ = _mock_client()
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        jobs = [
            JobCreate(
                title="Engineer", company="Corp", url="https://x.com/1",
                location=None, description="desc", employment_type=None,
                source=None, posted_at=None,
            )
        ]
        await database.add_jobs(jobs)

        mock_client.table.assert_called_with("job_listings")
        chain.upsert.assert_called_once()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  add_resume
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAddResume:
    @pytest.mark.asyncio
    async def test_upserts_resume_text(self, monkeypatch):
        from app.db import database
        mock_client, chain, _ = _mock_client()
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        await database.add_resume("My resume text", "user-123")

        mock_client.table.assert_called_with("user_profiles")
        call_args = chain.upsert.call_args[0][0]
        assert call_args["id"] == "user-123"
        assert call_args["resume_text"] == "My resume text"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  add_user_profile
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAddUserProfile:
    @pytest.mark.asyncio
    async def test_pops_email_before_upsert(self, monkeypatch):
        from app.db import database
        mock_client, chain, _ = _mock_client()
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        profile = {"id": "user-1", "full_name": "Test", "email": "test@test.com"}
        await database.add_user_profile(profile)

        call_args = chain.upsert.call_args[0][0]
        assert "email" not in call_args
        assert call_args["full_name"] == "Test"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  get_jobs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetJobs:
    @pytest.mark.asyncio
    async def test_no_embedding_raises_404(self, monkeypatch):
        from app.db import database

        mock_client, _, execute_result = _mock_client(return_data=[])
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        with pytest.raises(HTTPException) as exc_info:
            await database.get_jobs("user-no-embed")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_null_embedding_raises_404(self, monkeypatch):
        from app.db import database

        mock_client, _, _ = _mock_client(return_data=[{"embedding": None}])
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        with pytest.raises(HTTPException) as exc_info:
            await database.get_jobs("user-null-embed")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_jobs_from_rpc(self, monkeypatch):
        from app.db import database

        embedding = [0.1] * 384

        # First call: select embedding
        select_chain = MagicMock()
        select_result = MagicMock()
        select_result.data = [{"embedding": embedding}]
        for m in ("select", "eq"):
            getattr(select_chain, m).return_value = select_chain
        select_chain.execute = AsyncMock(return_value=select_result)

        # Second call: RPC
        rpc_chain = MagicMock()
        rpc_result = MagicMock()
        rpc_result.data = [{"id": "job-1", "title": "Engineer"}]
        rpc_chain.execute = AsyncMock(return_value=rpc_result)

        mock_client = AsyncMock()
        mock_client.table = MagicMock(return_value=select_chain)
        mock_client.rpc = MagicMock(return_value=rpc_chain)

        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        jobs = await database.get_jobs("user-1")
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Engineer"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  get_user_profile_data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetUserProfileData:
    @pytest.mark.asyncio
    async def test_not_found_raises_404(self, monkeypatch):
        from app.db import database
        mock_client, _, _ = _mock_client(return_data=[])
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        with pytest.raises(HTTPException) as exc_info:
            await database.get_user_profile_data("missing-user")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_profile_dict(self, monkeypatch):
        from app.db import database

        profile = {"id": "u1", "full_name": "Alice", "skills": ["Python"]}
        mock_client, _, _ = _mock_client(return_data=[profile])
        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        result = await database.get_user_profile_data("u1")
        assert result["full_name"] == "Alice"
        assert result["skills"] == ["Python"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  get_similarity_score
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetSimilarityScore:
    @pytest.mark.asyncio
    async def test_returns_float_from_rpc_list(self, monkeypatch):
        from app.db import database

        embedding = [0.1] * 384

        select_chain = MagicMock()
        select_result = MagicMock()
        select_result.data = [{"embedding": embedding}]
        for m in ("select", "eq"):
            getattr(select_chain, m).return_value = select_chain
        select_chain.execute = AsyncMock(return_value=select_result)

        rpc_chain = MagicMock()
        rpc_result = MagicMock()
        rpc_result.data = [0.85]
        rpc_chain.execute = AsyncMock(return_value=rpc_result)

        mock_client = AsyncMock()
        mock_client.table = MagicMock(return_value=select_chain)
        mock_client.rpc = MagicMock(return_value=rpc_chain)

        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        score = await database.get_similarity_score("user-1", "job-1")
        assert score == 0.85
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_rpc_data(self, monkeypatch):
        from app.db import database

        embedding = [0.1] * 384

        select_chain = MagicMock()
        select_result = MagicMock()
        select_result.data = [{"embedding": embedding}]
        for m in ("select", "eq"):
            getattr(select_chain, m).return_value = select_chain
        select_chain.execute = AsyncMock(return_value=select_result)

        rpc_chain = MagicMock()
        rpc_result = MagicMock()
        rpc_result.data = None
        rpc_chain.execute = AsyncMock(return_value=rpc_result)

        mock_client = AsyncMock()
        mock_client.table = MagicMock(return_value=select_chain)
        mock_client.rpc = MagicMock(return_value=rpc_chain)

        monkeypatch.setattr(database, "_get_client", AsyncMock(return_value=mock_client))

        score = await database.get_similarity_score("user-1", "job-1")
        assert score == 0.0
