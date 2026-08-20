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
from agents.department_representative_agent import (
    DepartmentRepresentativeAgent
)


class NegotiationOrchestrator:

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        self.session_manager = SessionManager()

        self.conversation_manager = (
            ConversationManager()
        )

        self.agreement_detector = (
            AgreementDetector()
        )

        self.deadlock_detector = (
            DeadlockDetector()
        )

        self.report_generator = (
            ReportGenerator()
        )

        # --------------------------------------------------------
        # AGENTS
        # --------------------------------------------------------

        self.supplier_agent = SupplierAgent()
        self.hr_agent = HRAgent()
        self.budget_agent = BudgetAgent()

        # Implementation class remains DepartmentRepresentativeAgent,
        # but user-facing role is Budget Requester.
        self.department_agent = (
            DepartmentRepresentativeAgent()
        )

        self.buyer_agent = BuyerAgent()
        self.candidate_agent = CandidateAgent()

    # ============================================================
    # START NEGOTIATION
    # ============================================================

    def start(
        self,
        request: NegotiationRequest
    ):

        session_id = (
            self.session_manager.create_session(
                request.scenario,
                request.mode,
                request.max_rounds,
                request.agent1_config,
                request.agent2_config,
                request.project_total_budget
            )
        )

        self.conversation_manager.create_conversation(
            session_id
        )

        return {
            "session_id": session_id,
            "status": "success",
            "message": (
                f"Negotiation started for "
                f"'{request.scenario}' "
                f"in {request.mode} mode."
            )
        }

    # ============================================================
    # SPEAKER HELPERS
    # ============================================================

    def _get_speaker_names(self, scenario):

        if scenario == "Vendor Pricing Negotiation":
            return [
                "Buyer",
                "Supplier"
            ]

        if scenario == "Job Offer Negotiation":
            return [
                "Candidate",
                "HR Manager"
            ]

        if scenario == "Project Budget Allocation":
            return [
                "Budget Requester",
                "Budget Allocator"
            ]

        return []

    # ============================================================
    # GET AGENT FOR SPEAKER
    # ============================================================

    def _get_agent_for_speaker(
        self,
        scenario,
        speaker,
        agent1_config,
        agent2_config
    ):

        if scenario == "Vendor Pricing Negotiation":

            if speaker == "Buyer":
                return (
                    self.buyer_agent,
                    agent1_config
                )

            if speaker == "Supplier":
                return (
                    self.supplier_agent,
                    agent2_config
                )

        if scenario == "Job Offer Negotiation":

            if speaker == "Candidate":
                return (
                    self.candidate_agent,
                    agent1_config
                )

            if speaker == "HR Manager":
                return (
                    self.hr_agent,
                    agent2_config
                )

        if scenario == "Project Budget Allocation":

            if speaker == "Budget Requester":
                return (
                    self.department_agent,
                    agent1_config
                )

            if speaker == "Budget Allocator":
                return (
                    self.budget_agent,
                    agent2_config
                )

        raise ValueError(
            f"Unsupported scenario/speaker combination: "
            f"{scenario} / {speaker}"
        )

    # ============================================================
    # NEXT SPEAKER
    # ============================================================

    def _get_next_speaker(
        self,
        scenario,
        last_speaker
    ):

        # ========================================================
        # VENDOR PRICING
        # ========================================================

        if scenario == "Vendor Pricing Negotiation":

            if last_speaker == "Supplier":
                return "Buyer"

            if last_speaker == "Buyer":
                return "Supplier"

            # No previous message.
            # Supplier opens the negotiation.
            return "Supplier"

        # ========================================================
        # JOB OFFER
        # ========================================================

        if scenario == "Job Offer Negotiation":

            if last_speaker == "HR Manager":
                return "Candidate"

            if last_speaker == "Candidate":
                return "HR Manager"

            # No previous message.
            # HR opens the negotiation.
            return "HR Manager"

        # ========================================================
        # PROJECT BUDGET
        # ========================================================

        if scenario == "Project Budget Allocation":

            if last_speaker == "Budget Requester":
                return "Budget Allocator"

            if last_speaker == "Budget Allocator":
                return "Budget Requester"

            # No previous message.
            # Budget Requester opens the negotiation.
            return "Budget Requester"

        return None

    # ============================================================
    # OPENING MESSAGE
    # ============================================================

    def _create_opening_message(
        self,
        session_id,
        scenario,
        agent1_config,
        agent2_config
    ):

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        if len(conversation) > 0:
            return

        # ========================================================
        # VENDOR PRICING
        # ========================================================

        if scenario == "Vendor Pricing Negotiation":

            supplier_price = (
                agent2_config.starting_target
                if agent2_config
                else 105000
            )

            opening_message = (
                f"We are pleased to open discussions with "
                f"an offer of 100 units at "
                f"₹{supplier_price:,.0f} per unit. "
                f"We are open to discussing the commercial "
                f"terms to find a workable arrangement."
            )

            self.conversation_manager.add_message(
                session_id,
                "Supplier",
                opening_message
            )

            return

        # ========================================================
        # JOB OFFER
        # ========================================================

        if scenario == "Job Offer Negotiation":

            hr_salary = (
                agent2_config.starting_target
                if agent2_config
                else 1000000
            )

            hr_salary_lpa = (
                hr_salary / 100000
            )

            opening_message = (
                f"We are pleased to begin the discussion with "
                f"a starting salary offer of "
                f"₹{hr_salary_lpa:g} LPA. "
                f"We would be happy to discuss the overall "
                f"package and find a suitable arrangement."
            )

            self.conversation_manager.add_message(
                session_id,
                "HR Manager",
                opening_message
            )

            return

        # ========================================================
        # PROJECT BUDGET
        # ========================================================

        if scenario == "Project Budget Allocation":

            requester_budget = (
                agent1_config.starting_target
                if agent1_config
                else 3000000
            )

            opening_message = (
                f"We would like to begin the discussion with "
                f"an initial budget request of "
                f"₹{requester_budget:,.0f}. "
                f"This reflects the resources we believe are "
                f"needed to meet the project's key priorities. "
                f"We are open to discussing the allocation "
                f"and finding a practical solution."
            )

            self.conversation_manager.add_message(
                session_id,
                "Budget Requester",
                opening_message
            )

            return

    # ============================================================
    # EXPLICIT ACCEPTANCE
    # ============================================================

    def _is_explicit_acceptance(
        self,
        message
    ):
        """
        Detect genuine acceptance.

        IMPORTANT:
        Proposal language must NOT be treated as acceptance.

        Example:
            "Would you consider ₹96,500?"
        -> False

        Example:
            "We happily accept your offer of ₹96,500."
        -> True

        Example:
            "We confirm our agreement at ₹96,500."
        -> True
        """

        if not message:
            return False

        text = " ".join(
            str(message)
            .lower()
            .strip()
            .split()
        )

        # --------------------------------------------------------
        # FIRST: PROPOSAL LANGUAGE
        # --------------------------------------------------------
        #
        # These phrases indicate that negotiation is still active.
        #

        proposal_phrases = [

            "could we agree",
            "can we agree",
            "would you agree",
            "would you consider",
            "could you consider",
            "can we meet",
            "could we meet",
            "perhaps we can",
            "maybe we can",
            "we propose",
            "i propose",
            "we suggest",
            "i suggest",
            "we could compromise",
            "could we compromise",
            "would you be able",
            "can you consider",
            "please consider",

            "we are prepared to",
            "we are willing to",
            "we can move to",
            "we can adjust to",
            "we can offer",
            "we could move to",
            "we could offer",

            "would you be willing",
            "would you be prepared",
            "could you meet",
            "can you meet",
            "shall we meet",
            "let us meet",

            "i would propose",
            "i would suggest",
            "we would propose",
            "we would suggest"
        ]

        if any(
            phrase in text
            for phrase in proposal_phrases
        ):
            return False

        # --------------------------------------------------------
        # EXPLICIT ACCEPTANCE PHRASES
        # --------------------------------------------------------

        acceptance_phrases = [

            # Basic acceptance
            "we accept",
            "i accept",
            "we happily accept",
            "i happily accept",
            "we gladly accept",
            "i gladly accept",
            "we are happy to accept",
            "i am happy to accept",
            "we are pleased to accept",
            "i am pleased to accept",

            # Agreement
            "we agree to",
            "i agree to",
            "we agree on",
            "i agree on",
            "we agree",
            "i agree",

            "we confirm the agreement",
            "i confirm the agreement",
            "we confirm our agreement",
            "i confirm our agreement",

            "we confirm the deal",
            "i confirm the deal",
            "we confirm our deal",
            "i confirm our deal",

            # Finalization
            "we can finalize the agreement",
            "i can finalize the agreement",
            "we are ready to finalize",
            "i am ready to finalize",
            "we will finalize the agreement",
            "i will finalize the agreement",

            "we are happy to finalize",
            "i am happy to finalize",

            "we are pleased to finalize",
            "i am pleased to finalize",

            "we can finalize",
            "i can finalize",
            "we will finalize",
            "i will finalize",

            # Explicit completion
            "we have an agreement",
            "i have an agreement",
            "we have reached an agreement",
            "i have reached an agreement",

            "agreement is confirmed",
            "our agreement is confirmed",
            "the agreement is confirmed",

            "deal is confirmed",
            "the deal is confirmed",
            "deal confirmed",

            "we are pleased to confirm",
            "i am pleased to confirm",

            "we are delighted to confirm",
            "i am delighted to confirm",

            "we are delighted to have reached an agreement",
            "i am delighted to have reached an agreement",

            "we are delighted to have successfully concluded",
            "we have successfully concluded the agreement",

            # Final acceptance wording
            "that works for us",
            "that works for me",
            "this works for us",
            "this works for me",

            "we accept your offer",
            "i accept your offer",
            "we happily accept your offer",
            "i happily accept your offer",

            "we accept your proposal",
            "i accept your proposal",

            "we agree to your offer",
            "i agree to your offer",

            "we agree to your proposal",
            "i agree to your proposal",

            "we are happy with this offer",
            "i am happy with this offer",

            "we are satisfied with this offer",
            "i am satisfied with this offer"
        ]

        # --------------------------------------------------------
        # DIRECT PHRASE MATCH
        # --------------------------------------------------------

        if any(
            phrase in text
            for phrase in acceptance_phrases
        ):
            return True

        # --------------------------------------------------------
        # STRONG ACCEPTANCE COMBINATIONS
        # --------------------------------------------------------
        #
        # Helps catch natural LLM language such as:
        #
        # "We happily accept your offer..."
        # "We gladly accept..."
        # "We confirm that we have an agreement..."
        #

        acceptance_words = [
            "accept",
            "accepted",
            "acceptance"
        ]

        confirmation_words = [
            "confirm",
            "confirmed",
            "confirmation"
        ]

        agreement_words = [
            "agreement",
            "deal",
            "final agreement"
        ]

        final_words = [
            "finalize",
            "finalised",
            "finalized",
            "conclude",
            "concluded",
            "conclusion"
        ]

        has_acceptance_word = any(
            word in text
            for word in acceptance_words
        )

        has_confirmation_word = any(
            word in text
            for word in confirmation_words
        )

        has_agreement_word = any(
            word in text
            for word in agreement_words
        )

        has_final_word = any(
            word in text
            for word in final_words
        )

        # Strong acceptance:
        #
        # accept + offer/proposal/agreement/deal
        #
        if has_acceptance_word and (
            "offer" in text
            or "proposal" in text
            or has_agreement_word
            or "terms" in text
        ):
            return True

        # confirm + agreement/deal
        if has_confirmation_word and (
            has_agreement_word
            or "terms" in text
            or "offer" in text
        ):
            return True

        # finalize/conclude + agreement/deal
        if has_final_word and (
            has_agreement_word
            or "terms" in text
            or "deal" in text
        ):
            return True

        return False

    # ============================================================
    # DEADLOCK DETECTION
    # ============================================================

    def _is_repeated_deadlock(
        self,
        conversation,
        valid_speakers
    ):

        messages = [
            msg
            for msg in conversation
            if msg["speaker"] in valid_speakers
        ]

        if len(messages) < 8:
            return False

        recent = messages[-6:]

        if len(recent) < 6:
            return False

        normalized = []

        for msg in recent:

            text = (
                msg["message"]
                .lower()
                .strip()
            )

            normalized.append(
                " ".join(text.split())
            )

        unique_count = len(
            set(normalized)
        )

        if unique_count <= 2:
            return True

        deadlock_phrases = [
            "cannot compromise further",
            "cannot move further",
            "no further movement",
            "no further compromise",
            "cannot reach an agreement",
            "unable to reach an agreement",
            "irreconcilable",
            "deadlock",
            "no agreement is possible"
        ]

        deadlock_count = 0

        for msg in recent:

            text = msg["message"].lower()

            if any(
                phrase in text
                for phrase in deadlock_phrases
            ):
                deadlock_count += 1

        return deadlock_count >= 2

    # ============================================================
    # MARK AGREEMENT AND STOP
    # ============================================================

    def _complete_agreement(
        self,
        session_id,
        speaker,
        message
    ):

        # ========================================================
        # SAVE SYSTEM COMPLETION MESSAGE
        # ========================================================

        self.conversation_manager.add_message(
            session_id,
            "System",
            "Negotiation completed successfully. Agreement reached."
        )

        # ========================================================
        # UPDATE STATUS
        # ========================================================

        self.session_manager.update_status(
            session_id,
            "agreement_reached"
        )

        # ========================================================
        # CALCULATE ROUNDS
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        valid_speakers = (
            self._get_speaker_names(
                self.session_manager
                .get_session(session_id)
                .get("scenario")
            )
        )

        turn_count = sum(
            1
            for msg in conversation
            if msg.get("speaker") in valid_speakers
        )

        rounds = turn_count // 2

        # ========================================================
        # SAVE ROUND COUNT
        # ========================================================

        self.session_manager.update_status(
            session_id,
            "agreement_reached",
            rounds=rounds
        )

        # ========================================================
        # SAVE REPORT TO DATABASE
        # ========================================================

        self._save_completed_negotiation(
            session_id
        )

        # ========================================================
        # RESPONSE
        # ========================================================

        return {
            "session_id": session_id,
            "status": "agreement_reached",
            "speaker": speaker,
            "message": message,
            "round": rounds
        }


    # ============================================================
    # GENERATE REPORT
    # ============================================================

    def generate_report(
        self,
        session_id
    ):

        # ========================================================
        # GET SESSION
        # ========================================================

        session = (
            self.session_manager.get_session(
                session_id
            )
        )

        if session is None:

            return {
                "error": "Invalid session ID"
            }

        # ========================================================
        # GET CONVERSATION
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        if conversation is None:
            conversation = []

        # ========================================================
        # SESSION DATA
        # ========================================================

        scenario = session.get(
            "scenario",
            ""
        )

        status = session.get(
            "status",
            "in_progress"
        )

        agent1_config = session.get(
            "agent1_config"
        )

        agent2_config = session.get(
            "agent2_config"
        )

        # ========================================================
        # GENERATE REPORT
        # ========================================================

        report = self.report_generator.generate_report(

            session_id=session_id,

            conversation=conversation,

            status=status,

            scenario=scenario,

            agent1_config=agent1_config,

            agent2_config=agent2_config
        )

        return report


    # ============================================================
    # SAVE COMPLETED NEGOTIATION
    # ============================================================

    def _save_completed_negotiation(
        self,
        session_id
    ):

        session = (
            self.session_manager.get_session(
                session_id
            )
        )

        if session is None:
            return None

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        if conversation is None:
            conversation = []

        report = self.report_generator.generate_report(

            session_id=session_id,

            conversation=conversation,

            status=session.get(
                "status",
                "in_progress"
            ),

            scenario=session.get(
                "scenario",
                ""
            ),

            agent1_config=session.get(
                "agent1_config"
            ),

            agent2_config=session.get(
                "agent2_config"
            )
        )

        return (
            self.session_manager
            .save_completed_session(

                session_id=session_id,

                negotiation_score=report.get(
                    "negotiation_score"
                ),

                score_breakdown=report.get(
                    "score_breakdown"
                ),

                summary=report.get(
                    "summary"
                )
            )
        )

    # ============================================================
    # SINGLE AI TURN
    # ============================================================

    def simulate_next_turn(
        self,
        session_id
    ):

        session = (
            self.session_manager.get_session(
                session_id
            )
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

        # ========================================================
        # ALREADY COMPLETED
        # ========================================================

        if session.get("status") != "in_progress":

            return {
                "status": session["status"],
                "scenario": session["scenario"],
                "max_rounds": session["max_rounds"],
                "conversation": conversation
            }

        scenario = session["scenario"]
        max_rounds = session["max_rounds"]

        agent1_config = session.get(
            "agent1_config"
        )

        agent2_config = session.get(
            "agent2_config"
        )

        # ========================================================
        # CREATE OPENING MESSAGE
        # ========================================================

        if len(conversation) == 0:

            self._create_opening_message(
                session_id,
                scenario,
                agent1_config,
                agent2_config
            )

            conversation = (
                self.conversation_manager
                .get_conversation(session_id)
            )

            # Opening message is the first negotiation turn.
            # Return immediately so the frontend can display it.
            opening_message = conversation[-1]

            return {
                "session_id": session_id,
                "status": "in_progress",
                "speaker": opening_message["speaker"],
                "message": opening_message["message"],
                "round": 1,
                "max_rounds": max_rounds
            }

        # ========================================================
        # DETERMINE NEXT SPEAKER
        # ========================================================

        valid_speakers = (
            self._get_speaker_names(
                scenario
            )
        )

        negotiation_messages = [
            msg
            for msg in conversation
            if msg["speaker"] in valid_speakers
        ]

        last_speaker = (
            negotiation_messages[-1]["speaker"]
            if negotiation_messages
            else None
        )

        ai_speaker = (
            self._get_next_speaker(
                scenario,
                last_speaker
            )
        )

        if ai_speaker is None:

            return {
                "error": (
                    "Unable to determine "
                    "next negotiation speaker."
                )
            }

        # ========================================================
        # GET AGENT
        # ========================================================

        agent, agent_config = (
            self._get_agent_for_speaker(
                scenario,
                ai_speaker,
                agent1_config,
                agent2_config
            )
        )

        # ========================================================
        # GENERATE AI RESPONSE
        # ========================================================

        try:

            ai_response = agent.negotiate(
                conversation,
                scenario,
                agent_config
            )

            ai_reply = ai_response["message"]

        except Exception as e:

            print(
                "AI Error:",
                e
            )

            ai_reply = (
                "I appreciate your position. "
                "Let us continue working toward a "
                "practical solution."
            )

        # ========================================================
        # GEMINI QUOTA
        # ========================================================

        if (
            "RESOURCE_EXHAUSTED"
            in ai_reply
            or "429"
            in ai_reply
        ):

            self.conversation_manager.add_message(
                session_id,
                "System",
                (
                    "Simulation stopped because "
                    "the Gemini API quota was exceeded."
                )
            )

            self.session_manager.update_status(
                session_id,
                "quota_exceeded"
            )

            return {
                "session_id": session_id,
                "status": "quota_exceeded",
                "speaker": "System",
                "message": (
                    "Gemini API quota exceeded."
                )
            }

        # ========================================================
        # SAVE AI MESSAGE
        # ========================================================

        self.conversation_manager.add_message(
            session_id,
            ai_speaker,
            ai_reply
        )

        # ========================================================
        # EXPLICIT AGREEMENT
        # ========================================================

        if self._is_explicit_acceptance(
            ai_reply
        ):

            return self._complete_agreement(
                session_id,
                ai_speaker,
                ai_reply
            )

        # ========================================================
        # REFRESH
        # ========================================================

        conversation = (
            self.conversation_manager
            .get_conversation(session_id)
        )

        # ========================================================
        # DEADLOCK
        # ========================================================

        if self._is_repeated_deadlock(
            conversation,
            valid_speakers
        ):

            self.conversation_manager.add_message(
                session_id,
                "System",
                "Negotiation ended due to a prolonged deadlock."
            )

            self.session_manager.update_status(
                session_id,
                "deadlock"
            )

            self._save_completed_negotiation(
                session_id
            )

            return {
                "session_id": session_id,
                "status": "deadlock",
                "speaker": ai_speaker,
                "message": ai_reply
            }

        # ========================================================
        # COUNT TURNS
        # ========================================================

        turn_count = len([
            msg
            for msg in conversation
            if msg["speaker"] in valid_speakers
        ])

        completed_rounds = (
            turn_count // 2
        )

        # ========================================================
        # MAX ROUNDS
        # ========================================================

        if completed_rounds >= max_rounds:

            self.conversation_manager.add_message(
                session_id,
                "System",
                (
                    f"Negotiation ended after "
                    f"reaching the maximum of "
                    f"{max_rounds} rounds."
                )
            )

            self.session_manager.update_status(
                session_id,
                "max_rounds_reached",
                rounds=completed_rounds
            )

            self._save_completed_negotiation(
                session_id
            )

            return {
                "session_id": session_id,
                "status": "max_rounds_reached",
                "speaker": ai_speaker,
                "message": ai_reply,
                "round": completed_rounds,
                "max_rounds": max_rounds
            }

        # ========================================================
        # CONTINUE
        # ========================================================

        return {
            "session_id": session_id,
            "status": "in_progress",
            "speaker": ai_speaker,
            "message": ai_reply,
            "round": completed_rounds,
            "max_rounds": max_rounds
        }

    # ============================================================
    # FULL AI VS AI SIMULATION
    # ============================================================

    def simulate_negotiation(
        self,
        session_id
    ):

        session = (
            self.session_manager.get_session(
                session_id
            )
        )

        if session is None:

            return {
                "error": "Invalid session"
            }

        scenario = session["scenario"]
        mode = session["mode"]
        max_rounds = session["max_rounds"]

        # ========================================================
        # ALREADY COMPLETE
        # ========================================================

        if session.get("status") != "in_progress":

            conversation = (
                self.conversation_manager
                .get_conversation(session_id)
            )

            return {
                "status": session["status"],
                "scenario": scenario,
                "mode": mode,
                "max_rounds": max_rounds,
                "conversation": conversation
            }

        # ========================================================
        # CREATE OPENING
        # ========================================================

        conversation = (
            self.conversation_manager
            .get_conversation(session_id)
        )

        if len(conversation) == 0:

            self._create_opening_message(
                session_id,
                scenario,
                session.get("agent1_config"),
                session.get("agent2_config")
            )

        # ========================================================
        # STRICT ZIG-ZAG LOOP
        # ========================================================

        for _ in range(max_rounds * 2):

            result = (
                self.simulate_next_turn(
                    session_id
                )
            )

            status = result.get(
                "status"
            )

            # ----------------------------------------------------
            # STOP IMMEDIATELY
            # ----------------------------------------------------

            if status in [
                "agreement_reached",
                "deadlock",
                "max_rounds_reached",
                "quota_exceeded"
            ]:
                break

            if status != "in_progress":
                break

        # ========================================================
        # FINAL SESSION
        # ========================================================

        session = (
            self.session_manager.get_session(
                session_id
            )
        )

        conversation = (
            self.conversation_manager
            .get_conversation(session_id)
        )

        # ========================================================
        # SAFETY FALLBACK
        # ========================================================

        if session.get("status") == "in_progress":

            self.conversation_manager.add_message(
                session_id,
                "System",
                (
                    f"Negotiation ended after reaching "
                    f"the maximum of {max_rounds} rounds."
                )
            )

            self.session_manager.update_status(
                session_id,
                "max_rounds_reached"
            )

            session = (
                self.session_manager.get_session(
                    session_id
                )
            )

        return {
            "status": session["status"],
            "scenario": scenario,
            "mode": mode,
            "max_rounds": max_rounds,
            "conversation": conversation
        }

    # ============================================================
    # HUMAN VS AI
    # ============================================================

    def next_round(
        self,
        request
    ):

        session = (
            self.session_manager.get_session(
                request.session_id
            )
        )

        if session is None:

            return {
                "error": "Invalid session ID"
            }

        # ========================================================
        # DO NOT ACCEPT AFTER COMPLETION
        # ========================================================

        if session.get("status") != "in_progress":

            return {
                "session_id": request.session_id,
                "status": session["status"],
                "message": (
                    "This negotiation has already ended."
                )
            }

        # ========================================================
        # SAVE USER MESSAGE
        # ========================================================

        self.conversation_manager.add_message(
            request.session_id,
            request.speaker,
            request.message
        )

        conversation = (
            self.conversation_manager.get_conversation(
                request.session_id
            )
        )

        scenario = session["scenario"]
        max_rounds = session["max_rounds"]

        # ========================================================
        # HUMAN AGREEMENT
        # ========================================================

        if self._is_explicit_acceptance(
            request.message
        ):

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
                    if request.speaker
                    == "Budget Requester"
                    else "Budget Requester"
                )

            else:

                ai_speaker = "AI"

            final_reply = (
                "Thank you. We are pleased to confirm "
                "that we have reached an agreement."
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

            valid_speakers = (
                self._get_speaker_names(
                    scenario
                )
            )

            current_round = (
                sum(
                    1
                    for message in conversation
                    if message["speaker"]
                    in valid_speakers
                )
                // 2
            )

            return {
                "session_id": request.session_id,
                "status": "agreement_reached",
                "speaker": ai_speaker,
                "message": final_reply,
                "round": current_round,
                "max_rounds": max_rounds
            }

        # ========================================================
        # DEADLOCK
        # ========================================================

        valid_speakers = (
            self._get_speaker_names(
                scenario
            )
        )

        if self._is_repeated_deadlock(
            conversation,
            valid_speakers
        ):

            self.session_manager.update_status(
                request.session_id,
                "deadlock"
            )

            return {
                "session_id": request.session_id,
                "status": "deadlock",
                "message": (
                    "Negotiation ended after a prolonged "
                    "lack of movement."
                )
            }

        # ========================================================
        # AGENT CONFIG
        # ========================================================

        agent1_config = session.get(
            "agent1_config"
        )

        agent2_config = session.get(
            "agent2_config"
        )

        # ========================================================
        # SELECT OPPOSITE AI
        # ========================================================

        if scenario == "Vendor Pricing Negotiation":

            if request.speaker == "Buyer":

                agent = self.supplier_agent
                ai_speaker = "Supplier"
                agent_config = agent2_config

            else:

                agent = self.buyer_agent
                ai_speaker = "Buyer"
                agent_config = agent1_config

        elif scenario == "Job Offer Negotiation":

            if request.speaker == "Candidate":

                agent = self.hr_agent
                ai_speaker = "HR Manager"
                agent_config = agent2_config

            else:

                agent = self.candidate_agent
                ai_speaker = "Candidate"
                agent_config = agent1_config

        elif scenario == "Project Budget Allocation":

            if request.speaker == "Budget Requester":

                agent = self.budget_agent
                ai_speaker = "Budget Allocator"
                agent_config = agent2_config

            else:

                agent = self.department_agent
                ai_speaker = "Budget Requester"
                agent_config = agent1_config

        else:

            raise ValueError(
                f"Unsupported scenario: {scenario}"
            )

        # ========================================================
        # AI RESPONSE
        # ========================================================

        try:

            ai_response = agent.negotiate(
                conversation,
                scenario,
                agent_config
            )

            ai_reply = ai_response["message"]

        except Exception as e:

            print(
                "AI Error:",
                e
            )

            ai_reply = (
                "I appreciate your position. "
                "Let us continue working toward a "
                "practical solution."
            )

        # ========================================================
        # SAVE AI MESSAGE
        # ========================================================

        self.conversation_manager.add_message(
            request.session_id,
            ai_speaker,
            ai_reply
        )

        # ========================================================
        # EXPLICIT AI AGREEMENT
        # ========================================================

        if self._is_explicit_acceptance(
            ai_reply
        ):

            return self._complete_agreement(
                request.session_id,
                ai_speaker,
                ai_reply
            )

        # ========================================================
        # REFRESH
        # ========================================================

        conversation = (
            self.conversation_manager
            .get_conversation(
                request.session_id
            )
        )

        # ========================================================
        # MAX ROUNDS
        # ========================================================

        current_round = (
            sum(
                1
                for message in conversation
                if message["speaker"]
                in valid_speakers
            )
            // 2
        )

        if current_round >= max_rounds:

            self.session_manager.update_status(
                request.session_id,
                "max_rounds_reached"
            )

            self.conversation_manager.add_message(
                request.session_id,
                "System",
                (
                    f"Negotiation ended after "
                    f"reaching the maximum of "
                    f"{max_rounds} rounds."
                )
            )

            return {
                "session_id": request.session_id,
                "status": "max_rounds_reached",
                "scenario": scenario,
                "round": current_round,
                "max_rounds": max_rounds,
                "speaker": "System",
                "message": (
                    f"The maximum of {max_rounds} "
                    f"negotiation rounds has been reached."
                )
            }

        # ========================================================
        # CONTINUE
        # ========================================================

        return {
            "session_id": request.session_id,
            "speaker": ai_speaker,
            "message": ai_reply,
            "status": "in_progress",
            "round": current_round,
            "max_rounds": max_rounds
        }