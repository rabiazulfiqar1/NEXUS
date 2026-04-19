from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List
from uuid import UUID

class UserBase(BaseModel):
    full_name: str
    skills: List[str] = Field(default_factory=list)
    degree: str | None
    graduation_year: int | None
    experience: List[dict] = Field(default_factory=list)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    resume_text: str | None
    created_at: datetime 

