from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager
from backend.conversation_manager import ConversationManager
from backend.agreement_detector import AgreementDetector
from backend.deadlock_detector import DeadlockDetector
from backend.report_generator import ReportGenerator


class NegotiationOrchestrator:

    def __init__(self):
        self.session_manager = SessionManager()
        self.conversation_manager = ConversationManager()
        self.agreement_detector = AgreementDetector()
        self.deadlock_detector = DeadlockDetector()
        self.report_generator = ReportGenerator()

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

        conversation = self.conversation_manager.get_conversation(request.session_id)

        if self.agreement_detector.is_agreement(request.message):
            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": request.speaker,
                "message": "Negotiation completed successfully."
            }
        if self.deadlock_detector.is_deadlock(conversation):
            return {
                "session_id": request.session_id,
                "status": "deadlock",
                "message": "Negotiation ended without agreement."
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
    def generate_report(self, session_id):

        conversation = self.conversation_manager.get_conversation(session_id)

        if not conversation:
            return {
            "error": "Session not found"
        }

        status = "completed"

        return self.report_generator.generate_report(
                    session_id,
                    conversation,
                    status
                    )