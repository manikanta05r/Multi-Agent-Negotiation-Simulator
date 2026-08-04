from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager
from backend.conversation_manager import ConversationManager
from backend.agreement_detector import AgreementDetector
from backend.deadlock_detector import DeadlockDetector
from backend.report_generator import ReportGenerator
from agents.supplier_agent import SupplierAgent
from agents.hr_agent import HRAgent
from agents.budget_agent import BudgetAgent


class NegotiationOrchestrator:

    def __init__(self):
        self.session_manager = SessionManager()
        self.conversation_manager = ConversationManager()
        self.agreement_detector = AgreementDetector()
        self.deadlock_detector = DeadlockDetector()
        self.report_generator = ReportGenerator()
        self.supplier_agent = SupplierAgent()
        self.hr_agent = HRAgent()
        self.budget_agent = BudgetAgent()

    def start(self, request: NegotiationRequest):
        session_id = self.session_manager.create_session(
            request.scenario,
            request.mode,
            request.max_rounds
        )

        # Create an empty conversation for this session
        self.conversation_manager.create_conversation(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Negotiation started for '{request.scenario}' in {request.mode} mode."
        }

    def next_round(self, request):

        # Save buyer message
        self.conversation_manager.add_message(
            request.session_id,
            request.speaker,
            request.message
        )

        # Get conversation history
        conversation = self.conversation_manager.get_conversation(
            request.session_id
        )
        # Get session details
        session = self.session_manager.get_session(request.session_id)
        if session is None:
            return {
                "error": "Invalid session ID"
            }

        scenario = session["scenario"]
        mode = session["mode"]
        max_rounds = session["max_rounds"]

       # Count buyer messages (each buyer message = one round)
        current_round = sum(
            1 for message in conversation
            if message["speaker"].lower() == "buyer"
        )

        # Stop if maximum rounds exceeded
        if current_round > max_rounds:

            self.session_manager.update_status(
                request.session_id,
                "max_rounds_reached"
            )



            # Save final system message
            self.conversation_manager.add_message(
                request.session_id,
                "System",
                f"Negotiation ended after reaching the maximum of {max_rounds} rounds."
            )

            return {
                "session_id": request.session_id,
                "status": "max_rounds_reached",
                "scenario": scenario,
                "rounds_completed": current_round,
                "max_rounds": max_rounds,
                "speaker": "System",
                "message": (
                    f"The maximum of {max_rounds} negotiation rounds has been reached. "
                    "The negotiation has ended without an agreement."
                )
            }

        # Check agreement
        if self.agreement_detector.is_agreement(request.message):

            final_prompt = conversation + [
                {
                    "speaker": "System",
                    "message": (
                        "The buyer has accepted the final offer. "
                        "Generate a short professional closing message "
                        "confirming the agreement. "
                        "Do not continue negotiating."
                    )
                }
            ]

            try:
                final_reply = (
                    "Thank you for the successful negotiation. "
                    "We are pleased to confirm our agreement. "
                    "We look forward to working with you."
                )

            except Exception as e:
                print("AI Error:", e)

                final_reply = (
                    "Thank you for the successful negotiation. "
                    "We are pleased to confirm the agreement. "
                    "We look forward to doing business with you."
                )

            # Save supplier closing message
            self.conversation_manager.add_message(
                request.session_id,
                "Supplier",
                final_reply
            )

            self.session_manager.update_status(
                request.session_id,
                "agreement_reached"
            )

            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": "Supplier",
                "message": final_reply
            }

        # Check deadlock
        if self.deadlock_detector.is_deadlock(conversation):

            self.session_manager.update_status(
                request.session_id,
                "deadlock"
            )

            return {
                "session_id": request.session_id,
                "status": "deadlock",
                "message": "Negotiation ended without agreement."
            }

        # Normal AI response
        try:

            if scenario == "Vendor Pricing Negotiation":
                ai_response = self.supplier_agent.negotiate(
                    conversation,
                    scenario
                )

            elif scenario == "Job Offer Negotiation":
                ai_response = self.hr_agent.negotiate(
                    conversation,
                    scenario
                )

            elif scenario == "Project Budget Allocation":
                    ai_response = self.budget_agent.negotiate(
                        conversation,
                        scenario
                    )

            else:
                raise ValueError(f"Unsupported scenario: {scenario}")

            ai_reply = ai_response["message"]

        except Exception as e:
            print("AI Error:", e)

            ai_reply = (
                "I'm unable to generate a response at the moment. "
                "Please continue the negotiation."
            )

        # Save AI reply
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

        session = self.session_manager.get_session(session_id)

        if session is None:
            return {
                "error": "Session not found"
            }

        scenario = session["scenario"]
        status = session.get("status", "completed")

        return self.report_generator.generate_report(
            session_id,
            conversation,
            status,
            scenario
        )