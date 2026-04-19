from fastapi import FastAPI
from app.routers import users, jobs

app = FastAPI()

app.include_router(users.router, prefix="/api/v1", tags=["users"])