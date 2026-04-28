from pydantic import BaseModel, Field


class ResumeEnhanceRequest(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=120)


class ResumeEnhanceResponse(BaseModel):
    mode: str
    target_role: str
    summary: str
    improved_bullets: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class CVGenerateRequest(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=120)


class CVGenerateResponse(BaseModel):
    mode: str
    target_role: str
    professional_summary: str
    skills: list[str] = Field(default_factory=list)
    experience_bullets: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
