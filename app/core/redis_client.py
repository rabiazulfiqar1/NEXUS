import redis.asyncio as aioredis
from app.core.config import REDIS_URL

_redis: aioredis.Redis | None = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis

async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None