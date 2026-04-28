from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import supabase
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from app.db.async_client import get_async_client
from supabase._async.client import AsyncClient

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

oauth_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth_scheme),
                           client: AsyncClient = Depends(get_async_client)):
    token = credentials.credentials
    try:
        user = await client.auth.get_user(token)
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user.user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user_from_request(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    client = await get_async_client()
    user = await client.auth.get_user(token)
    return user.user if user.user else None
