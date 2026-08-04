from typing import Any
from database.connection import supabase

def fetch_all_todos() -> list[dict[str, Any]]:
    """Fetch all records from the 'todos' table."""
    response = supabase.table('todos').select("*").execute()
    data = response.data or []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []

def add_todo(name: str) -> dict[str, Any] | None:
    """Insert a new record into the 'todos' table."""
    response = supabase.table('todos').insert({"name": name}).execute()
    data = response.data or []
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data[0]
    return None
