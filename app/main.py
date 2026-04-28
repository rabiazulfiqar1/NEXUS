from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, jobs, resume_tools
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.job_fetcher import fetch_jobs
from app.db.async_client import get_async_client
from app.core.dependencies import get_current_user_from_request
from app.core.redis_client import get_redis, close_redis

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_async_client()
    await get_redis()
    scheduler.add_job(fetch_jobs, trigger='cron', day_of_week='mon', hour=7, minute=45)
    scheduler.start()
    yield
    scheduler.shutdown()
    await close_redis()

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def attach_user(request: Request, call_next):
    try:
        user = await get_current_user_from_request(request)
        request.state.user = user
    except Exception:
        request.state.user = None
    return await call_next(request)

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