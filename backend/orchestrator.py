from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager
from backend.conversation_manager import ConversationManager


class NegotiationOrchestrator:

    def __init__(self):
        self.session_manager = SessionManager()
        self.conversation_manager = ConversationManager()

    def start(self, request: NegotiationRequest):
        session_id = self.session_manager.create_session()

        # Create an empty conversation for this session
        self.conversation_manager.create_conversation(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Negotiation started for '{request.scenario}' in {request.mode} mode."
        }

    def next_round(self, request):
        # Save the user's message
        self.conversation_manager.add_message(
            request.session_id,
            request.speaker,
            request.message
        )

        # Dummy AI response
        ai_reply = "Your offer is too low. I can reduce the price slightly."

        # Save the AI response
        self.conversation_manager.add_message(
            request.session_id,
            "Supplier",
            ai_reply
        )

        return {
            "session_id": request.session_id,
            "speaker": "Supplier",
            "message": ai_reply
        }