import uuid

from database.operations import (
    save_negotiation,
    fetch_completed_negotiations,
    fetch_negotiation,
)


class SessionManager:

    def __init__(self):
        # Keep in-memory storage for active negotiations.
        self.sessions = {}

    def create_session(
        self,
        scenario,
        mode,
        max_rounds,
        agent1_config=None,
        agent2_config=None,
        project_total_budget=None
    ):
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "scenario": scenario,
            "mode": mode,
            "max_rounds": max_rounds,
            "agent1_config": agent1_config,
            "agent2_config": agent2_config,
            "project_total_budget": project_total_budget,
            "status": "in_progress"
        }

        return session_id

    def get_session(self, session_id):

        # First check active in-memory sessions.
        session = self.sessions.get(session_id)

        if session is not None:
            return session

        # If it is not active, try the database.
        return fetch_negotiation(session_id)

    def update_status(
        self,
        session_id,
        status,
        rounds=None
    ):

        if session_id not in self.sessions:
            return

        self.sessions[session_id]["status"] = status

        if rounds is not None:
            self.sessions[session_id]["rounds"] = rounds

    def save_completed_session(
        self,
        session_id,
        negotiation_score=None,
        score_breakdown=None,
        summary=None
    ):
        """
        Save a completed negotiation to Supabase.
        """

        session = self.sessions.get(session_id)

        if session is None:
            return None

        rounds = session.get("rounds", 0)

        return save_negotiation(
            session_id=session_id,
            scenario=session["scenario"],
            mode=session["mode"],
            max_rounds=session["max_rounds"],
            status=session["status"],
            rounds=rounds,
            project_total_budget=session.get(
                "project_total_budget"
            ),
            negotiation_score=negotiation_score,
            score_breakdown=score_breakdown,
            summary=summary
        )

    def get_completed_sessions(self):

        # Database is now the source of persistent history.
        return fetch_completed_negotiations()