from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, jobs, resume_tools

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(resume_tools.router, prefix="/api/v1", tags=["resume-tools"])