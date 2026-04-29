# app/core/redis_client.py

import redis.asyncio as aioredis
from app.core.config import REDIS_URL

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    """
    Returns a singleton Redis client.
    If Redis is down, returns None instead of crashing.
    """
    global _redis

    if _redis is None:
        try:
            _redis = aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
            )

            # 🔥 verify connection immediately
            await _redis.ping()

        except Exception as e:
            print(f"[Redis Warning] Connection failed: {e}")
            _redis = None
            return None

    return _redis


async def close_redis():
    """Gracefully close Redis connection on shutdown"""
    global _redis

    if _redis:
        try:
            await _redis.close()
        except Exception:
            pass
        finally:
            _redis = None