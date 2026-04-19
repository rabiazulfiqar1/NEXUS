from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import supabase
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

oauth_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth_scheme)):
    token = credentials.credentials
    try:
        user = supabase_client.auth.get_user(token)
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


