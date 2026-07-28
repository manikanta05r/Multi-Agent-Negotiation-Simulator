from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager


class NegotiationOrchestrator:

    def __init__(self):
        self.session_manager = SessionManager()

    def start(self, request: NegotiationRequest):

        session_id = self.session_manager.create_session()

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Negotiation started for '{request.scenario}' in {request.mode} mode."
        }