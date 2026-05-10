"""
Tests for Pydantic schemas: validation, defaults, and edge cases.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


# ── UserCreate / UserBase ─────────────────────────────────────────────────────

class TestUserSchemas:
    def test_user_create_valid_full(self):
        from app.schemas.user import UserCreate
        user = UserCreate(
            full_name="Alice",
            linkedin_url="https://linkedin.com/in/alice",
            github_url="https://github.com/alice",
            skills=["Python", "SQL"],
            degree="BS CS",
            graduation_year=2025,
            experience=[{"company": "Acme", "role": "Intern"}],
            projects=[{"name": "Portfolio"}],
            experience_years=1,
        )
        assert user.full_name == "Alice"
        assert len(user.skills) == 2

    def test_user_create_minimal(self):
        from app.schemas.user import UserCreate
        user = UserCreate()
        assert user.full_name is None
        assert user.skills == []
        assert user.experience == []
        assert user.projects == []
        assert user.experience_years is None

    def test_user_create_empty_skills_list(self):
        from app.schemas.user import UserCreate
        user = UserCreate(skills=[])
        assert user.skills == []

    def test_user_response_requires_id(self):
        from app.schemas.user import UserResponse
        with pytest.raises(ValidationError):
            UserResponse()  # missing required 'id'

    def test_user_response_valid(self):
        from app.schemas.user import UserResponse
        user = UserResponse(id="550e8400-e29b-41d4-a716-446655440000")
        assert user.email is None
        assert user.is_embed is None


# ── JobCreate / JobBase ───────────────────────────────────────────────────────

class TestJobSchemas:
    def test_job_create_valid(self):
        from app.schemas.job import JobCreate
        job = JobCreate(
            title="Backend Engineer",
            company="TechCorp",
            location="Remote",
            description="Python expert needed",
            employment_type="FULLTIME",
            source="LinkedIn",
            url="https://example.com/job/1",
            posted_at=datetime(2026, 1, 15),
        )
        assert job.title == "Backend Engineer"
        assert job.url == "https://example.com/job/1"

    def test_job_create_required_fields_only(self):
        from app.schemas.job import JobCreate
        job = JobCreate(
            title="Intern",
            company="StartupCo",
            url="https://startup.co/apply",
            location=None,
            description=None,
            employment_type=None,
            source=None,
            posted_at=None,
        )
        assert job.title == "Intern"
        assert job.posted_at is None

    def test_job_create_missing_title_raises(self):
        from app.schemas.job import JobCreate
        with pytest.raises(ValidationError):
            JobCreate(company="X", url="https://x.com")

    def test_job_create_missing_company_raises(self):
        from app.schemas.job import JobCreate
        with pytest.raises(ValidationError):
            JobCreate(title="Y", url="https://y.com")

    def test_job_create_missing_url_raises(self):
        from app.schemas.job import JobCreate
        with pytest.raises(ValidationError):
            JobCreate(title="Z", company="Z Corp")


# ── ResumeEnhanceRequest / Response ──────────────────────────────────────────

class TestResumeSchemas:
    def test_enhance_request_valid(self):
        from app.schemas.llm_resume import ResumeEnhanceRequest
        req = ResumeEnhanceRequest(target_role="Backend Engineer")
        assert req.target_role == "Backend Engineer"

    def test_enhance_request_too_short(self):
        from app.schemas.llm_resume import ResumeEnhanceRequest
        with pytest.raises(ValidationError):
            ResumeEnhanceRequest(target_role="A")  # min_length=2

    def test_enhance_request_too_long(self):
        from app.schemas.llm_resume import ResumeEnhanceRequest
        with pytest.raises(ValidationError):
            ResumeEnhanceRequest(target_role="X" * 121)  # max_length=120

    def test_enhance_response_defaults(self):
        from app.schemas.llm_resume import ResumeEnhanceResponse
        resp = ResumeEnhanceResponse(
            mode="mock",
            target_role="SWE",
            summary="Good candidate.",
        )
        assert resp.improved_bullets == []
        assert resp.missing_keywords == []
        assert resp.next_steps == []

    def test_cv_generate_request_valid(self):
        from app.schemas.llm_resume import CVGenerateRequest
        req = CVGenerateRequest(target_role="Data Scientist")
        assert req.target_role == "Data Scientist"

    def test_cv_generate_response_defaults(self):
        from app.schemas.llm_resume import CVGenerateResponse
        resp = CVGenerateResponse(
            mode="groq",
            target_role="ML Engineer",
            professional_summary="Strong ML background.",
        )
        assert resp.skills == []
        assert resp.experience_bullets == []
        assert resp.projects == []


# ── GeneratedCV (Crew output) ────────────────────────────────────────────────

class TestGeneratedCVSchema:
    """Only runs if crewai is installed."""

    @pytest.fixture(autouse=True)
    def _skip_if_no_crewai(self):
        pytest.importorskip("crewai", reason="crewai not installed")

    def test_generated_cv_valid(self):
        from app.services.crew.tasks import GeneratedCV
        cv = GeneratedCV(
            professional_summary="Excellent candidate.",
            skills=["Python"],
            experience_bullets=["Built APIs"],
            projects=["NEXUS"],
            ats_score=0.85,
            trending_skills_used=["Python"],
            skill_gaps_remaining=["AWS"],
        )
        assert cv.ats_score == 0.85

    def test_generated_cv_missing_required_field(self):
        from app.services.crew.tasks import GeneratedCV
        with pytest.raises(ValidationError):
            GeneratedCV(
                professional_summary="Test",
                skills=[],
                experience_bullets=[],
                projects=[],
                # missing ats_score, trending_skills_used, skill_gaps_remaining
            )

    def test_generated_cv_empty_lists(self):
        from app.services.crew.tasks import GeneratedCV
        cv = GeneratedCV(
            professional_summary="Candidate",
            skills=[],
            experience_bullets=[],
            projects=[],
            ats_score=0.0,
            trending_skills_used=[],
            skill_gaps_remaining=[],
        )
        assert cv.skills == []
        assert cv.ats_score == 0.0
