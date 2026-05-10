"""
Unit tests for app.services.resume_parser — embedding text builder,
skill extraction, and ATS scoring logic.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.resume_parser import build_user_embedding_text, extract_skills_with_llm


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  build_user_embedding_text
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestBuildUserEmbeddingText:
    def test_with_resume_text_returns_resume_text(self):
        profile = {"resume_text": "Full resume content here.", "skills": ["Python"]}
        assert build_user_embedding_text(profile) == "Full resume content here."

    def test_resume_text_whitespace_only_falls_through(self):
        profile = {
            "resume_text": "   ",
            "skills": ["Python"],
            "degree": "BS CS",
            "experience": [],
            "projects": [],
        }
        result = build_user_embedding_text(profile)
        assert "Python" in result
        assert "BS CS" in result

    def test_no_resume_text_builds_from_fields(self):
        profile = {
            "resume_text": None,
            "skills": ["Python", "FastAPI"],
            "degree": "BS CS",
            "experience": [{"company": "Acme", "role": "Intern"}],
            "projects": [{"name": "NEXUS", "tech": "FastAPI"}],
        }
        result = build_user_embedding_text(profile)
        assert "Python" in result
        assert "FastAPI" in result
        assert "BS CS" in result
        assert "Acme" in result
        assert "NEXUS" in result

    def test_empty_profile(self):
        profile = {}
        result = build_user_embedding_text(profile)
        assert result == ""

    def test_experience_years_included_when_present(self):
        profile = {
            "resume_text": None,
            "skills": [],
            "degree": None,
            "experience": [],
            "projects": [],
            "experience_years": 3,
        }
        result = build_user_embedding_text(profile)
        assert "Experience Years: 3" in result

    def test_experience_years_excluded_when_none(self):
        profile = {
            "resume_text": None,
            "skills": [],
            "degree": None,
            "experience": [],
            "projects": [],
            "experience_years": None,
        }
        result = build_user_embedding_text(profile)
        assert "Experience Years" not in result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  extract_skills_with_llm (currently mocked in source)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestExtractSkillsWithLLM:
    def test_extracts_matching_skills(self):
        text = "Expert in Python and FastAPI development with Docker containers"
        skills = extract_skills_with_llm(text)
        assert "Python" in skills
        assert "FastAPI" in skills
        assert "Docker" in skills

    def test_partial_match(self):
        text = "Experience with React and web frameworks"
        skills = extract_skills_with_llm(text)
        assert "React" in skills

    def test_no_match_returns_fallback(self):
        text = "Experienced in gardening and cooking"
        skills = extract_skills_with_llm(text)
        # Should return the first 3 from mock_skills fallback
        assert len(skills) == 3
        assert isinstance(skills, list)

    def test_case_insensitive(self):
        text = "knowledge of python and rest api design"
        skills = extract_skills_with_llm(text)
        assert "Python" in skills
        assert "REST API" in skills

    def test_returns_list_type(self):
        result = extract_skills_with_llm("anything")
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ats_score (mocked DB calls)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAtsScore:
    @pytest.mark.asyncio
    async def test_ats_score_computes_weighted_average(self, monkeypatch):
        from app.services import resume_parser

        # Mock get_similarity_score
        monkeypatch.setattr(
            resume_parser, "get_similarity_score",
            AsyncMock(return_value=0.8),
        )

        # Mock supabase_client.table(...).select(...).eq(...).execute()
        mock_user_chain = MagicMock()
        mock_user_result = MagicMock()
        mock_user_result.data = [{"resume_text": "Python FastAPI Docker", "skills": ["Python", "FastAPI"]}]
        mock_user_chain.select.return_value = mock_user_chain
        mock_user_chain.eq.return_value = mock_user_chain
        mock_user_chain.execute.return_value = mock_user_result

        mock_job_chain = MagicMock()
        mock_job_result = MagicMock()
        mock_job_result.data = [{"description": "Need Python FastAPI Docker REST API skills"}]
        mock_job_chain.select.return_value = mock_job_chain
        mock_job_chain.eq.return_value = mock_job_chain
        mock_job_chain.execute.return_value = mock_job_result

        call_count = {"n": 0}
        def mock_table(name):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return mock_user_chain
            return mock_job_chain

        monkeypatch.setattr(resume_parser, "supabase_client", MagicMock(table=mock_table))

        score = await resume_parser.ats_score("user-1", "job-1")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_ats_score_user_not_found_raises(self, monkeypatch):
        from app.services import resume_parser
        from fastapi import HTTPException

        monkeypatch.setattr(
            resume_parser, "get_similarity_score",
            AsyncMock(return_value=0.5),
        )

        mock_chain = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_chain.select.return_value = mock_chain
        mock_chain.eq.return_value = mock_chain
        mock_chain.execute.return_value = mock_result

        monkeypatch.setattr(resume_parser, "supabase_client", MagicMock(table=lambda _: mock_chain))

        with pytest.raises(HTTPException) as exc_info:
            await resume_parser.ats_score("bad-user", "job-1")
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_ats_score_no_job_description_returns_sim_score(self, monkeypatch):
        from app.services import resume_parser

        monkeypatch.setattr(
            resume_parser, "get_similarity_score",
            AsyncMock(return_value=0.75),
        )

        mock_user_chain = MagicMock()
        mock_user_result = MagicMock()
        mock_user_result.data = [{"resume_text": "Python dev", "skills": ["Python"]}]
        mock_user_chain.select.return_value = mock_user_chain
        mock_user_chain.eq.return_value = mock_user_chain
        mock_user_chain.execute.return_value = mock_user_result

        mock_job_chain = MagicMock()
        mock_job_result = MagicMock()
        mock_job_result.data = [{"description": None}]
        mock_job_chain.select.return_value = mock_job_chain
        mock_job_chain.eq.return_value = mock_job_chain
        mock_job_chain.execute.return_value = mock_job_result

        call_count = {"n": 0}
        def mock_table(name):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return mock_user_chain
            return mock_job_chain

        monkeypatch.setattr(resume_parser, "supabase_client", MagicMock(table=mock_table))

        score = await resume_parser.ats_score("user-1", "job-1")
        # When no job description, should return only similarity score
        assert score == 0.75
