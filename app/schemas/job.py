from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class JobBase(BaseModel):
    title: str
    company: str
    location: str | None
    description: str | None
    employment_type: str | None
    source: str | None
    url: str 
    posted_at: datetime | None

class JobCreate(JobBase):
    pass

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    fetched_at: datetime

