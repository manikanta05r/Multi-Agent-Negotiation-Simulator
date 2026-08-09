from typing import Any, Dict, List, Optional

from database.connection import get_supabase_client
from database.models import NegotiationMessage, NegotiationSession


def create_session(session: NegotiationSession) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        response = client.table("negotiation_sessions").insert(session.__dict__).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        response = client.table("negotiation_sessions").select("*").eq("id", session_id).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None


def update_session_status(session_id: str, status: str) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        response = client.table("negotiation_sessions").update({"status": status}).eq("id", session_id).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None


def add_message(message: NegotiationMessage) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        response = client.table("negotiation_messages").insert(message.__dict__).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None


def get_messages(session_id: str) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return []

    try:
        response = client.table("negotiation_messages").select("*").eq("session_id", session_id).execute()
        return response.data or []
    except Exception:
        return []
