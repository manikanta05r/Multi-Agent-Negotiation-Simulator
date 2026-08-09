import os
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Create and cache a Supabase client from environment variables."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip()

    if not supabase_url or not supabase_key:
        return None

    try:
        _supabase_client = create_client(supabase_url, supabase_key)
    except Exception as exc:
        print(f"Supabase client creation failed: {exc}")
        return None

    return _supabase_client


def is_supabase_available() -> bool:
    return get_supabase_client() is not None
