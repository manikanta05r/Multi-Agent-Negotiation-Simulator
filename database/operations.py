from typing import Any

from database.connection import supabase


# ============================================================
# NEGOTIATION OPERATIONS
# ============================================================

def save_negotiation(
    session_id: str,
    scenario: str,
    mode: str,
    max_rounds: int,
    status: str,
    rounds: int = 0,
    project_total_budget: float | None = None,
    negotiation_score: float | None = None,
    score_breakdown: dict[str, Any] | None = None,
    summary: str | None = None,
) -> dict[str, Any] | None:
    """
    Save or update a completed negotiation in Supabase.
    """

    data = {
        "session_id": session_id,
        "scenario": scenario,
        "mode": mode,
        "max_rounds": max_rounds,
        "status": status,
        "rounds": rounds,
        "project_total_budget": project_total_budget,
        "negotiation_score": negotiation_score,
        "score_breakdown": score_breakdown,
        "summary": summary,
    }

    response = (
        supabase
        .table("negotiations")
        .upsert(
            data,
            on_conflict="session_id"
        )
        .execute()
    )

    result = response.data or []

    if (
        isinstance(result, list)
        and len(result) > 0
        and isinstance(result[0], dict)
    ):
        return result[0]

    return None


def fetch_completed_negotiations() -> list[dict[str, Any]]:
    """
    Fetch all completed negotiations from Supabase.
    """

    response = (
        supabase
        .table("negotiations")
        .select("*")
        .neq("status", "in_progress")
        .order("created_at", desc=True)
        .execute()
    )

    data = response.data or []

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    return []


def fetch_negotiation(
    session_id: str
) -> dict[str, Any] | None:
    """
    Fetch one negotiation using its session ID.
    """

    response = (
        supabase
        .table("negotiations")
        .select("*")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )

    data = response.data or []

    if (
        isinstance(data, list)
        and len(data) > 0
        and isinstance(data[0], dict)
    ):
        return data[0]

    return None


# ============================================================
# NEGOTIATION MESSAGE OPERATIONS
# ============================================================

def save_negotiation_message(
    session_id: str,
    speaker: str,
    message: str,
) -> dict[str, Any] | None:
    """
    Save one conversation message for a negotiation.
    """

    data = {
        "session_id": session_id,
        "speaker": speaker,
        "message": message,
    }

    response = (
        supabase
        .table("negotiation_messages")
        .insert(data)
        .execute()
    )

    result = response.data or []

    if (
        isinstance(result, list)
        and len(result) > 0
        and isinstance(result[0], dict)
    ):
        return result[0]

    return None


def fetch_negotiation_messages(
    session_id: str
) -> list[dict[str, Any]]:
    """
    Fetch all conversation messages for a negotiation.
    """

    response = (
        supabase
        .table("negotiation_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    data = response.data or []

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    return []

def delete_negotiation(
    session_id: str
) -> bool:
    """
    Delete a negotiation and its messages
    using the session ID.
    """

    # Delete related messages first
    supabase \
        .table("negotiation_messages") \
        .delete() \
        .eq("session_id", session_id) \
        .execute()

    # Delete the negotiation
    response = (
        supabase
        .table("negotiations")
        .delete()
        .eq("session_id", session_id)
        .execute()
    )

    return bool(response.data)

def save_negotiation_message(
    session_id: str,
    speaker: str,
    message: str
) -> dict[str, Any] | None:
    """Save a negotiation message to Supabase."""

    response = (
        supabase
        .table("negotiation_messages")
        .insert({
            "session_id": session_id,
            "speaker": speaker,
            "message": message
        })
        .execute()
    )

    data = response.data or []

    if (
        isinstance(data, list)
        and len(data) > 0
        and isinstance(data[0], dict)
    ):
        return data[0]

    return None


def fetch_negotiation_messages(
    session_id: str
) -> list[dict[str, Any]]:
    """Fetch all messages for a negotiation."""

    response = (
        supabase
        .table("negotiation_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    data = response.data or []

    if isinstance(data, list):
        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    return []