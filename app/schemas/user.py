from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List
from uuid import UUID

class UserBase(BaseModel):
    full_name: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    skills: List[str] = Field(default_factory=list)
    degree: str | None = None
    graduation_year: int | None = None
    experience: List[dict] = Field(default_factory=list)
    projects: List[dict] = Field(default_factory=list)
    experience_years: int | None = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str | None = None
    resume_text: str | None = None
    is_embed: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

