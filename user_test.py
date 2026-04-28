# test.py mein
from supabase import create_client
from app.core.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
res = client.auth.sign_in_with_password({"email": "rzulfiqar889@gmail.com", "password": "Rabiazulfiqar123"})
print(res.session.access_token)