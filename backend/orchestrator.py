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
from agents.department_representative_agent import DepartmentRepresentativeAgent


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
        self.department_agent = DepartmentRepresentativeAgent()
        self.buyer_agent = BuyerAgent()
        self.candidate_agent = CandidateAgent()

    def start(self, request: NegotiationRequest):

        session_id = self.session_manager.create_session(
            request.scenario,
            request.mode,
            request.max_rounds,
            request.agent1_config,
            request.agent2_config,
            request.project_total_budget
        )

        self.conversation_manager.create_conversation(session_id)

        return {
            "session_id": session_id,
            "status": "success",
            "message": f"Negotiation started for '{request.scenario}' in {request.mode} mode."
        }

    def next_round(self, request):

        session = self.session_manager.get_session(
            request.session_id
        )

        if session is None:
            return {"error": "Invalid session ID"}

        # Stop immediately if negotiation is already completed
        if session.get("status") != "in_progress":
            return {
                "session_id": request.session_id,
                "status": session.get("status"),
                "message": "Negotiation has already ended. Further offers are disabled.",
                "round": session.get("rounds", 0),
                "max_rounds": session.get("max_rounds"),
                "conversation": self.conversation_manager.get_conversation(
                    request.session_id
                )
            }

        # Save user message only while negotiation is active
        self.conversation_manager.add_message(
            request.session_id,
            request.speaker,
            request.message
        )

        conversation = self.conversation_manager.get_conversation(
            request.session_id
        )

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

                ai_speaker = (
                    "Budget Allocator"
                    if request.speaker == "Budget Requester"
                    else "Budget Requester"
                )

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

            current_round = sum(
                1
                for message in conversation
                if message["speaker"] in [
                    "Buyer",
                    "Supplier",
                    "Candidate",
                    "HR Manager",
                    "Budget Requester",
                    "Budget Allocator"
                ]
            ) // 2

            self.session_manager.update_status(
                request.session_id,
                "agreement_reached",
                rounds=current_round
            )

            self._store_negotiation_score(
                request.session_id
            )


            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": ai_speaker,
                "message": final_reply,
                "round": current_round,
                "max_rounds": max_rounds
            }



        # Deadlock
        if self.deadlock_detector.is_deadlock(conversation):

            current_round = sum(
                1
                for message in conversation
                if message["speaker"] in [
                    "Buyer",
                    "Supplier",
                    "Candidate",
                    "HR Manager",
                    "Budget Requester",
                    "Budget Allocator"
                ]
            ) // 2


            self.session_manager.update_status(
                request.session_id,
                "deadlock",
                rounds=current_round
            )

            self._store_negotiation_score(
                request.session_id
            )

            return {
                "session_id": request.session_id,
                "status": "deadlock",
                "message": "Negotiation ended without agreement.",
                "round": current_round,
                "max_rounds": max_rounds
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

                if request.speaker == "Budget Requester":

                    ai_response = self.budget_agent.negotiate(
                        conversation,
                        scenario,
                        session.get("agent2_config")
                    )

                    ai_speaker = "Budget Allocator"

                else:

                    ai_response = self.department_agent.negotiate(
                        conversation,
                        scenario,
                        session.get("agent1_config")
                    )

                    ai_speaker = "Budget Requester"

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
        # Simulation already completed
        if session.get("status") != "in_progress":

            return {

                "status": session.get("status"),

                "scenario": session["scenario"],

                "mode": session["mode"],

                "max_rounds": session["max_rounds"],

                "conversation": conversation

            }

        negotiation_speakers = [
            "Buyer",
            "Supplier",
            "Candidate",
            "HR Manager",
            "Budget Requester",
            "Budget Allocator"
        ]

        current_round = sum(
            1
            for message in conversation
            if message["speaker"] in negotiation_speakers
        ) // 2

        print(f"Current Round: {current_round} / {max_rounds}")

        # Maximum rounds reached
        if current_round >= max_rounds:


            self.session_manager.update_status(
                request.session_id,
                "max_rounds_reached",
                rounds=current_round
            )

            self._store_negotiation_score(
                request.session_id
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
                "round": current_round,
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
            "message": ai_reply,
            "status": "in_progress",
            "round": current_round,
            "max_rounds": max_rounds
        }
    def simulate_next_turn(self, session_id):

        session = self.session_manager.get_session(session_id)

        if session is None:
            return {
                "error": "Invalid session ID"
            }

        conversation = self.conversation_manager.get_conversation(
            session_id
        )

        # ---------------------------------
        # Already completed?
        # ---------------------------------

        if session.get("status") != "in_progress":
            return {
                "status": session["status"],
                "scenario": session["scenario"],
                "max_rounds": session["max_rounds"],
                "conversation": conversation
            }

        scenario = session["scenario"]
        max_rounds = session["max_rounds"]

        agent1_config = session.get("agent1_config")
        agent2_config = session.get("agent2_config")

        # ---------------------------------
        # Make sure opening message exists
        # ---------------------------------

        if len(conversation) == 0:

            if scenario == "Vendor Pricing Negotiation":

                supplier_price = (
                    agent2_config.starting_target
                    if agent2_config
                    else 105000
                )

                self.conversation_manager.add_message(
                    session_id,
                    "Supplier",
                    f"We are pleased to offer 100 laptops at ₹{supplier_price:,.0f} per unit with standard warranty and delivery."
                )

            elif scenario == "Job Offer Negotiation":

                hr_salary = (
                    agent2_config.starting_target
                    if agent2_config
                    else 1000000
                )

                hr_salary_lpa = hr_salary / 100000

                self.conversation_manager.add_message(
                    session_id,
                    "HR Manager",
                    f"We are pleased to offer you a position with a salary of ₹{hr_salary_lpa:g} LPA along with standard company benefits."
                )

            elif scenario == "Project Budget Allocation":

                total_budget = session.get(
                    "project_total_budget"
                )

                if total_budget is None:
                    total_budget = 5000000

                total_budget_lakh = total_budget / 100000

                self.conversation_manager.add_message(
                    session_id,
                    "Budget Allocator",
                    f"The total project budget available is ₹{total_budget_lakh:g} lakh. Please present your department's budget requirements so we can reach a fair allocation."
                )

            conversation = self.conversation_manager.get_conversation(
                session_id
            )

        # ---------------------------------
        # Determine who should speak
        # ---------------------------------

        negotiation_speakers = [
            msg["speaker"]
            for msg in conversation
            if msg["speaker"] in [
                "Buyer",
                "Supplier",
                "Candidate",
                "HR Manager",
                "Budget Requester",
                "Budget Allocator"
            ]
        ]

        last_speaker = (
            negotiation_speakers[-1]
            if negotiation_speakers
            else None
        )

        # ---------------------------------
        # Select next AI agent
        # ---------------------------------

        if scenario == "Vendor Pricing Negotiation":

            if last_speaker == "Supplier":
                ai_speaker = "Buyer"
                agent = self.buyer_agent
                agent_config = agent1_config

            else:
                ai_speaker = "Supplier"
                agent = self.supplier_agent
                agent_config = agent2_config

        elif scenario == "Job Offer Negotiation":

            if last_speaker == "HR Manager":
                ai_speaker = "Candidate"
                agent = self.candidate_agent
                agent_config = agent1_config

            else:
                ai_speaker = "HR Manager"
                agent = self.hr_agent
                agent_config = agent2_config

        elif scenario == "Project Budget Allocation":

            if last_speaker == "Budget Allocator":
                ai_speaker = "Budget Requester"
                agent = self.department_agent
                agent_config = agent1_config

            else:
                ai_speaker = "Budget Allocator"
                agent = self.budget_agent
                agent_config = agent2_config

        else:
            return {
                "error": f"Unsupported scenario: {scenario}"
            }

        # ---------------------------------
        # Generate ONE AI response
        # ---------------------------------

        try:

            ai_response = agent.negotiate(
                conversation,
                scenario,
                agent_config
            )

            ai_reply = ai_response["message"]

        except Exception as e:

            print("AI Error:", e)

            ai_reply = (
                "I'm unable to generate a response at the moment. "
                "Please continue the negotiation."
            )

        # ---------------------------------
        # Gemini quota
        # ---------------------------------

        if (
            "RESOURCE_EXHAUSTED" in ai_reply
            or "429" in ai_reply
        ):

            self.conversation_manager.add_message(
                session_id,
                "System",
                "Simulation stopped because the Gemini API quota was exceeded."
            )

            self.session_manager.update_status(
                session_id,
                "quota_exceeded"
            )

            return {
                "session_id": session_id,
                "status": "quota_exceeded",
                "speaker": "System",
                "message": "Gemini API quota exceeded."
            }

        # ---------------------------------
        # Add ONE AI message
        # ---------------------------------

        self.conversation_manager.add_message(
            session_id,
            ai_speaker,
            ai_reply
        )

        conversation = self.conversation_manager.get_conversation(
            session_id
        )

        turn_count = len([
            msg
            for msg in conversation
            if msg["speaker"] in [
                "Buyer",
                "Supplier",
                "Candidate",
                "HR Manager",
                "Budget Requester",
                "Budget Allocator"
            ]
        ])

        completed_rounds = max(
            0,
            (turn_count + 1) // 2
        )

        # ---------------------------------
        # Agreement detection
        # ---------------------------------

        if self.agreement_detector.is_agreement(
            ai_reply
        ):

            self.conversation_manager.add_message(
                session_id,
                "System",
                "Negotiation completed successfully. Agreement reached."
            )

            self.session_manager.update_status(
                session_id,
                "agreement_reached",
                rounds=completed_rounds
            )

            self._store_negotiation_score(
                session_id
            )

            return {
                "session_id": session_id,
                "status": "agreement_reached",
                "speaker": ai_speaker,
                "message": ai_reply,
                "round": completed_rounds,
                "max_rounds": max_rounds
            }

        # ---------------------------------
        # Refresh conversation
        # ---------------------------------

        conversation = self.conversation_manager.get_conversation(
            session_id
        )

        # ---------------------------------
        # Deadlock detection
        # ---------------------------------

        if self.deadlock_detector.is_deadlock(
            conversation
        ):

            self.conversation_manager.add_message(
                session_id,
                "System",
                "Negotiation ended due to deadlock."
            )

            self.session_manager.update_status(
                session_id,
                "deadlock",
                rounds=completed_rounds
            )
            self._store_negotiation_score(
                session_id
            )

            return {
                "session_id": session_id,
                "status": "deadlock",
                "speaker": ai_speaker,
                "message": ai_reply,
                "round": completed_rounds,
                "max_rounds": max_rounds
            }

        # ---------------------------------
        # Maximum rounds
        # ---------------------------------

        if completed_rounds >= max_rounds:

            self.conversation_manager.add_message(
                session_id,
                "System",
                f"Negotiation ended after reaching the maximum of {max_rounds} rounds."
            )

            self.session_manager.update_status(
                session_id,
                "max_rounds_reached",
                rounds=max_rounds
            )

            self._store_negotiation_score(
                session_id
            )

            return {
                "session_id": session_id,
                "status": "max_rounds_reached",
                "speaker": ai_speaker,
                "message": ai_reply
            }

        # ---------------------------------
        # Continue negotiation
        # ---------------------------------

        return {
            "session_id": session_id,
            "status": "in_progress",
            "speaker": ai_speaker,
            "message": ai_reply,
            "round": completed_rounds
        }
    def simulate_negotiation(self, session_id):

        session = self.session_manager.get_session(session_id)

        if session is None:
            return {
                "error": "Invalid session"
            }

        conversation = self.conversation_manager.get_conversation(
            session_id
        )

        # -----------------------------
        # Already simulated?
        # -----------------------------

        if session.get("status") != "in_progress":
            return {
                "status": session["status"],
                "scenario": session["scenario"],
                "mode": session["mode"],
                "max_rounds": session["max_rounds"],
                "conversation": conversation
            }

        scenario = session["scenario"]
        mode = session["mode"]
        max_rounds = session["max_rounds"]
        agent1_config = session.get("agent1_config")
        agent2_config = session.get("agent2_config")


        # -----------------------------
        # Opening Message
        # -----------------------------

        if len(conversation) == 0:

            if scenario == "Vendor Pricing Negotiation":


                supplier_price = (
                    agent2_config.starting_target
                    if agent2_config
                    else 105000
                )

                self.conversation_manager.add_message(

                    session_id,

                    "Supplier",

                     f"We are pleased to offer 100 laptops at ₹{supplier_price:,.0f} per unit with standard warranty and delivery."

                )

            elif scenario == "Job Offer Negotiation":

                hr_salary = (
                        agent2_config.starting_target
                        if agent2_config
                        else 1000000
                    )
                
                hr_salary_lpa = hr_salary / 100000

                self.conversation_manager.add_message(

                    session_id,

                    "HR Manager",

                    f"We are pleased to offer you a position with a salary of ₹{hr_salary_lpa:g} LPA along with standard company benefits."

                )

            elif scenario == "Project Budget Allocation":

                total_budget = session.get(
                    "project_total_budget",
                    5000000
                )

                total_budget_lakh = total_budget / 100000

                self.conversation_manager.add_message(
                    session_id,
                    "Budget Allocator",
                    f"The total project budget available is ₹{total_budget_lakh:g} lakh. Please present your department's budget requirements so we can reach a fair allocation."
                )

            conversation = self.conversation_manager.get_conversation(
                session_id
            )
            print("\n========== Conversation after Opening ==========")

            for msg in conversation:
                print(msg["speaker"], ":", msg["message"])

            print("==============================================\n")

            # -----------------------------
            # Negotiation Loop
            # -----------------------------

        for round_number in range(max_rounds):

            current_round = round_number + 1

            conversation = self.conversation_manager.get_conversation(
                session_id
            )

            # -----------------------------
            # Buyer Turn
            # -----------------------------

            if scenario == "Vendor Pricing Negotiation":

                buyer_response = self.buyer_agent.negotiate(
                    conversation,
                    scenario,
                    agent1_config
                )

                buyer_reply = buyer_response["message"]

                # Gemini quota exceeded
                if (
                    "RESOURCE_EXHAUSTED" in buyer_reply
                    or "429" in buyer_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "Buyer",
                    buyer_reply
                )

                # Agreement reached?
                if self.agreement_detector.is_agreement(
                    buyer_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )
                    self._store_negotiation_score(
                        session_id
                    )

                    break


                conversation = self.conversation_manager.get_conversation(session_id)

                print("\n========== Conversation after Buyer ==========")

                for msg in conversation:
                    print(msg["speaker"], ":", msg["message"])

                print("=============================================\n")

                # -----------------------------
                # Supplier Turn
                # -----------------------------

                supplier_response = self.supplier_agent.negotiate(
                    conversation,
                    scenario,
                    agent2_config
                )

                supplier_reply = supplier_response["message"]

                # Gemini quota exceeded
                if (
                    "RESOURCE_EXHAUSTED" in supplier_reply
                    or "429" in supplier_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "Supplier",
                    supplier_reply
                )

                # Agreement reached?
                if self.agreement_detector.is_agreement(
                    supplier_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break
                # -----------------------------
                # Refresh Conversation
                # -----------------------------

                conversation = self.conversation_manager.get_conversation(
                    session_id
                )
                print("\n========== Conversation after Supplier ==========")

                for msg in conversation:
                    print(msg["speaker"], ":", msg["message"])

                print("================================================\n")

                # -----------------------------
                # Deadlock Detection
                # -----------------------------

                if self.deadlock_detector.is_deadlock(conversation):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation ended due to deadlock."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "deadlock",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break


            elif scenario == "Job Offer Negotiation":

                candidate_response = self.candidate_agent.negotiate(
                    conversation,
                    scenario,
                    agent1_config
                )

                candidate_reply = candidate_response["message"]

                if (
                    "RESOURCE_EXHAUSTED" in candidate_reply
                    or "429" in candidate_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "Candidate",
                    candidate_reply
                )

                if self.agreement_detector.is_agreement(candidate_reply):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break

                conversation = self.conversation_manager.get_conversation(
                    session_id
                )

                hr_response = self.hr_agent.negotiate(
                    conversation,
                    scenario,
                    agent2_config
                )

                hr_reply = hr_response["message"]

                if (
                    "RESOURCE_EXHAUSTED" in hr_reply
                    or "429" in hr_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "HR Manager",
                    hr_reply
                )
            

                if self.agreement_detector.is_agreement(hr_reply):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )


                    self._store_negotiation_score(
                        session_id
                    )

                    break

                conversation = self.conversation_manager.get_conversation(
                    session_id
                )

                if self.deadlock_detector.is_deadlock(conversation):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation ended due to deadlock."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "deadlock",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break            



            elif scenario == "Project Budget Allocation":

                department_response = self.department_agent.negotiate(
                    conversation,
                    scenario,
                    agent1_config
                )

                department_reply = department_response["message"]

                print("\nDepartment Reply:", department_reply)
                print(
                    "Agreement Detected:",
                    self.agreement_detector.is_agreement(department_reply)
                )

                if (
                    "RESOURCE_EXHAUSTED" in department_reply
                    or "429" in department_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "Budget Requester",
                    department_reply
                )

                if self.agreement_detector.is_agreement(department_reply):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break

                conversation = self.conversation_manager.get_conversation(
                    session_id
                )

                budget_response = self.budget_agent.negotiate(
                    conversation,
                    scenario,
                    agent2_config
                )

                budget_reply = budget_response["message"]

                print("\nBudget Reply:", budget_reply)
                print(
                    "Agreement Detected:",
                    self.agreement_detector.is_agreement(budget_reply)
                )

                if (
                    "RESOURCE_EXHAUSTED" in budget_reply
                    or "429" in budget_reply
                ):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Simulation stopped because the Gemini API quota was exceeded."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "quota_exceeded"
                    )

                    break

                self.conversation_manager.add_message(
                    session_id,
                    "Budget Allocator",
                    budget_reply
                )

                if self.agreement_detector.is_agreement(budget_reply):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation completed successfully. Agreement reached."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "agreement_reached",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break

                conversation = self.conversation_manager.get_conversation(
                    session_id
                )

                if self.deadlock_detector.is_deadlock(conversation):

                    self.conversation_manager.add_message(
                        session_id,
                        "System",
                        "Negotiation ended due to deadlock."
                    )

                    self.session_manager.update_status(
                        session_id,
                        "deadlock",
                        rounds=current_round
                    )

                    self._store_negotiation_score(
                        session_id
                    )

                    break







            # ---------------------------------
            # Loop Finished
            # ---------------------------------

        session = self.session_manager.get_session(session_id)

        # No status means maximum rounds reached
        if session.get("status") == "in_progress":

            self.conversation_manager.add_message(
                session_id,
                "System",
                f"Maximum of {max_rounds} rounds reached."
            )

            self.session_manager.update_status(
                session_id,
                "max_rounds_reached",
                rounds=current_round
            )

            self._store_negotiation_score(
                session_id
            )

            session = self.session_manager.get_session(
                session_id
            )

        conversation = self.conversation_manager.get_conversation(
            session_id
        )

        return {

            "status": session["status"],

            "scenario": scenario,

            "mode": mode,

            "max_rounds": max_rounds,

            "conversation": conversation

                }


    def _store_negotiation_score(self, session_id):

        try:
            report = self.generate_report(session_id)

            score = report.get(
                "negotiation_score"
            )

            score_breakdown = report.get(
                "score_breakdown"
            )

            summary = report.get(
                "summary"
            )

            # Store score in the active in-memory session.
            session = self.session_manager.get_session(
                session_id
            )

            if session is not None:

                session["negotiation_score"] = score

                session["score_breakdown"] = (
                    score_breakdown
                )

                session["summary"] = summary

            # Persist the completed negotiation
            # in Supabase.
            self.session_manager.save_completed_session(
                session_id=session_id,
                negotiation_score=score,
                score_breakdown=score_breakdown,
                summary=summary
            )

        except Exception as e:

            print(
                "Error storing negotiation score:",
                e
            )

    def generate_report(self, session_id):

        session = self.session_manager.get_session(
            session_id
        )

        if session is None:
            return {
                "error": "Invalid session ID"
            }

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        status = session.get(
            "status",
            "in_progress"
        )

        scenario = session.get(
            "scenario",
            "Unknown"
        )

        agent1_config = session.get("agent1_config")
        agent2_config = session.get("agent2_config")

        report = self.report_generator.generate_report(
            session_id,
            conversation,
            status,
            scenario,
            agent1_config,
            agent2_config
        )

        # Store the generated score in the session
        if "negotiation_score" in report:

            self.session_manager.sessions[
                session_id
            ]["negotiation_score"] = report[
                "negotiation_score"
            ]

        return report