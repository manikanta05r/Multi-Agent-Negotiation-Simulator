from schemas.negotiation import NegotiationRequest
from backend.session_manager import SessionManager
from backend.conversation_manager import ConversationManager
from backend.agreement_detector import AgreementDetector
from backend.deadlock_detector import DeadlockDetector
from backend.report_generator import ReportGenerator
from agents.supplier_agent import SupplierAgent
from agents.hr_agent import HRAgent
from agents.budget_agent import BudgetAgent
from agents.buyer_agent import BuyerAgent
from agents.candidate_agent import CandidateAgent


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
        self.buyer_agent = BuyerAgent()
        self.candidate_agent = CandidateAgent()

    def start(self, request: NegotiationRequest):

        session_id = self.session_manager.create_session(
            request.scenario,
            request.mode,
            request.max_rounds
        )

        self.conversation_manager.create_conversation(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Negotiation started for '{request.scenario}' in {request.mode} mode."
        }

    def next_round(self, request):

        # Save user message
        self.conversation_manager.add_message(
            request.session_id,
            request.speaker,
            request.message
        )

        conversation = self.conversation_manager.get_conversation(
            request.session_id
        )

        session = self.session_manager.get_session(request.session_id)

        if session is None:
            return {"error": "Invalid session ID"}

        scenario = session["scenario"]
        max_rounds = session["max_rounds"]

        # Agreement reached
        if self.agreement_detector.is_agreement(request.message):

            if scenario == "Vendor Pricing Negotiation":
                ai_speaker = (
                    "Supplier"
                    if request.speaker == "Buyer"
                    else "Buyer"
                )

            elif scenario == "Job Offer Negotiation":
                ai_speaker = (
                    "HR Manager"
                    if request.speaker == "Candidate"
                    else "Candidate"
                )

            elif scenario == "Project Budget Allocation":
                ai_speaker = "Budget Manager"

            else:
                ai_speaker = "AI"

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

            self.conversation_manager.add_message(
                request.session_id,
                ai_speaker,
                final_reply
            )

            self.session_manager.update_status(
                request.session_id,
                "agreement_reached"
            )

            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": ai_speaker,
                "message": final_reply
            }
        
            


        # Deadlock
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

        # AI Response
        try:

            if scenario == "Vendor Pricing Negotiation":

                if request.speaker == "Buyer":

                    ai_response = self.supplier_agent.negotiate(
                        conversation,
                        scenario
                    )

                    ai_speaker = "Supplier"

                else:

                    ai_response = self.buyer_agent.negotiate(
                        conversation,
                        scenario
                    )

                    ai_speaker = "Buyer"

            elif scenario == "Job Offer Negotiation":

                if request.speaker == "Candidate":

                    ai_response = self.hr_agent.negotiate(
                        conversation,
                        scenario
                    )

                    ai_speaker = "HR Manager"

                else:

                    ai_response = self.candidate_agent.negotiate(
                        conversation,
                        scenario
                    )
                    ai_speaker = "Candidate"

            elif scenario == "Project Budget Allocation":

                ai_response = self.budget_agent.negotiate(
                    conversation,
                    scenario
                )
                ai_speaker = "Budget Manager"

            else:

                raise ValueError(
                    f"Unsupported scenario: {scenario}"
                )

            ai_reply = ai_response["message"]

        except Exception as e:

            print("AI Error:", e)

            ai_reply = (
                "I'm unable to generate a response at the moment. "
                "Please continue the negotiation."
            )

        self.conversation_manager.add_message(
            request.session_id,
            ai_speaker,
            ai_reply
        )

        # Refresh conversation after AI reply
        conversation = self.conversation_manager.get_conversation(
            request.session_id
        )

        current_round = sum(
            1
            for message in conversation
            if message["speaker"] == request.speaker
        )

        print(f"Current Round: {current_round} / {max_rounds}")

        # Maximum rounds reached
        if current_round >= max_rounds:

            self.session_manager.update_status(
                request.session_id,
                "max_rounds_reached"
            )

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

        return {
            "session_id": request.session_id,
            "speaker": ai_speaker,
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