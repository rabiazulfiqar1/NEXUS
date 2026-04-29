import time
from fastapi import Request, HTTPException, status, Depends
from app.core.redis_client import get_redis
import uuid

# Per-route limits: (max_requests, window_seconds)
# RATE_LIMITS = {
#     "resume_enhance":  (5,  3600),   # 5/hour
#     "cv_generate":     (5,  3600),   # 5/hour
#     "ats_score":       (20, 3600),   # 20/hour
#     "jobs_list":       (60, 3600),   # 60/hour
#     "career_analyze":  (3,  3600),
# }

RATE_LIMITS = {
    "resume_enhance":  (50, 3600),   # was 5
    "cv_generate":     (50, 3600),   # was 5
    "ats_score":       (100, 3600),  # was 20
    "jobs_list":       (200, 3600),  # was 60
    "career_analyze":  (30, 3600),   # was 3
}

def _get_identifier(request: Request) -> str:
    """Use authenticated user ID if available, fall back to IP."""
    user = getattr(request.state, "user", None)
    return str(user.id) if user else request.client.host

async def check_rate_limit(key: str, max_requests: int, window: int, request: Request):
    """
    Sliding window log via Redis sorted set.
    
    Sorted set structure:
      - member: timestamp string (unique per request)
      - score:  timestamp (used for range queries)
    
    Each call:
      1. Remove all entries older than the window
      2. Add current timestamp
      3. Count remaining entries
      4. Reject if count exceeds limit
    """
    redis = await get_redis()
    identifier = _get_identifier(request)
    redis_key = f"rate_limit:{key}:{identifier}"
    current_time = int(time.time())
    window_start = current_time - window
    member = f"{current_time}:{uuid.uuid4()}"

    async with redis.pipeline(transaction=True) as pipe:
        await pipe.zremrangebyscore(redis_key, 0, window_start)   # evict expired
        await pipe.zadd(redis_key, {member: current_time})  # log request
        await pipe.zcard(redis_key)                                # count in window
        await pipe.expire(redis_key, window)                       # TTL cleanup
        _, _, count, _ = await pipe.execute()

    if count > max_requests:
        # Tell the client exactly when their oldest request expires
        oldest = await redis.zrange(redis_key, 0, 0, withscores=True)
        retry_after = int(oldest[0][1]) + window - current_time if oldest else window
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

# ── Dependency factories ──────────────────────────────────────────────────────
# Each returns a FastAPI dependency so routes stay clean

def rate_limit(route_key: str):
    """Usage: Depends(rate_limit('resume_enhance'))"""
    max_requests, window = RATE_LIMITS[route_key]

    async def _dependency(request: Request):
        await check_rate_limit(route_key, max_requests, window, request)

    return _dependency