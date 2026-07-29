from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager
from backend.conversation_manager import ConversationManager
from backend.agreement_detector import AgreementDetector

class NegotiationOrchestrator:

    def __init__(self):
        self.session_manager = SessionManager()
        self.conversation_manager = ConversationManager()
        self.agreement_detector = AgreementDetector()

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

        if self.agreement_detector.is_agreement(request.message):
            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": request.speaker,
                "message": "Negotiation completed successfully."
            }

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