import uuid


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(self, scenario, mode, max_rounds):
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "scenario": scenario,
            "mode": mode,
            "max_rounds": max_rounds
        }

        return session_id

    def get_session(self, session_id):
        return self.sessions.get(session_id)