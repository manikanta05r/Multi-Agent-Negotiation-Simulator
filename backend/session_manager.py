import uuid


class SessionManager:

    def create_session(self):
        return str(uuid.uuid4())