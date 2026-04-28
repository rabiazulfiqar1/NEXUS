from supabase._async.client import AsyncClient, create_client
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

_client: AsyncClient | None = None

async def get_async_client() -> AsyncClient:
    global _client
    if _client is None:
        _client = await create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client