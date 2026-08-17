import uuid


class SessionManager:

    def __init__(self):
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
        return self.sessions.get(session_id)


    def update_status(self, session_id, status):
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = status