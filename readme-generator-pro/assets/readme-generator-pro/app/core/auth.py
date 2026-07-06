SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
else:
    supabase = None


async def get_current_user(authorization: str = Header(None)):
    if not supabase:
        raise HTTPException(503, "Auth service not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please login first")
    token = authorization.split(" ", 1)[1]
    try:
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception:
        raise HTTPException(401, "Session expired, please login again")
import os
from fastapi import Header, HTTPException
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
   supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
else:
   supabase = None


async def get_current_user(authorization: str = Header(None)):
   if not supabase:
       raise HTTPException(503, "Auth service not configured")
   if not authorization or not authorization.startswith("Bearer "):
       raise HTTPException(401, "Please login first")
   token = authorization.split(" ", 1)[1]
   try:
       user = supabase.auth.get_user(token)
       return user.user.id
   except Exception:
       raise HTTPException(401, "Session expired, please login again")
import os
from fastapi import Header, HTTPException
from supabase import create_client, Client
