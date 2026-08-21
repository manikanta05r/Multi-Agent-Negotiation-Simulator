import re

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

        # Implementation class remains unchanged.
        # User-facing role is Budget Requester.
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
    # CONFIGURATION VALUE HELPER
    # ============================================================

    def _get_config_value(
        self,
        config,
        key,
        default=None
    ):
        """
        Read configuration values from either:

        - dictionary-based configs
        - Pydantic/object-based configs
        """

        if config is None:
            return default

        if isinstance(config, dict):
            return config.get(
                key,
                default
            )

        return getattr(
            config,
            key,
            default
        )

    # ============================================================
    # SPEAKER HELPERS
    # ============================================================

    def _get_speaker_names(
        self,
        scenario
    ):

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

            # Supplier opens.
            return "Supplier"

        # ========================================================
        # JOB OFFER
        # ========================================================

        if scenario == "Job Offer Negotiation":

            if last_speaker == "HR Manager":
                return "Candidate"

            if last_speaker == "Candidate":
                return "HR Manager"

            # HR opens.
            return "HR Manager"

        # ========================================================
        # PROJECT BUDGET
        # ========================================================

        if scenario == "Project Budget Allocation":

            if last_speaker == "Budget Requester":
                return "Budget Allocator"

            if last_speaker == "Budget Allocator":
                return "Budget Requester"

            # Budget Requester opens.
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
                self._get_config_value(
                    agent2_config,
                    "starting_target",
                    105000
                )
            )

            opening_message = (
                f"We are pleased to open discussions with "
                f"an offer of 100 units at "
                f"₹{float(supplier_price):,.0f} per unit. "
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
                self._get_config_value(
                    agent2_config,
                    "starting_target",
                    1000000
                )
            )

            hr_salary_lpa = (
                float(hr_salary) / 100000
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
                self._get_config_value(
                    agent1_config,
                    "starting_target",
                    3000000
                )
            )

            opening_message = (
                f"We would like to begin the discussion with "
                f"an initial budget request of "
                f"₹{float(requester_budget):,.0f}. "
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
    # MONEY EXTRACTION
    # ============================================================

    def _extract_last_money_value(
        self,
        message
    ):
        """
        Extract the final monetary value mentioned.

        Supports:
            ₹95,000
            ₹1,00,000
            ₹12 LPA
            ₹12 lakh
            95000 INR
            95000 rupees
        """

        if not message:
            return None

        text = str(message)

        patterns = [

            r"₹\s*([\d,]+(?:\.\d+)?)"
            r"\s*(LPA|lakhs?|lakh)?",

            r"([\d,]+(?:\.\d+)?)"
            r"\s*(LPA|lakhs?|lakh)\b",

            r"([\d,]+(?:\.\d+)?)"
            r"\s*(?:rupees|INR)\b",
        ]

        values = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                if isinstance(match, tuple):

                    raw_value = match[0]

                    unit = (
                        match[1]
                        if len(match) > 1
                        else ""
                    )

                else:

                    raw_value = match
                    unit = ""

                try:

                    value = float(
                        raw_value.replace(
                            ",",
                            ""
                        )
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                unit = (
                    unit or ""
                ).lower()

                if unit == "lpa":

                    value *= 100000

                elif unit in {
                    "lakh",
                    "lakhs"
                }:

                    value *= 100000

                values.append(
                    value
                )

        if not values:
            return None

        return values[-1]

    # ============================================================
    # LAST OFFER FROM OPPOSITE PARTY
    # ============================================================

    def _get_last_offer_from_speaker(
        self,
        conversation,
        speaker
    ):
        """
        Get the latest monetary value mentioned by a specific speaker.
        """

        for message in reversed(
            conversation
        ):

            if message.get(
                "speaker"
            ) != speaker:

                continue

            value = (
                self._extract_last_money_value(
                    message.get(
                        "message",
                        ""
                    )
                )
            )

            if value is not None:
                return value

        return None

    # ============================================================
    # AGREEMENT BOUNDARIES
    # ============================================================

    def _get_agreement_boundaries(
        self,
        session
    ):
        """
        Determine the valid agreement zone.

        Minimum-side roles:
            Supplier
            Candidate
            Budget Requester

        Maximum-side roles:
            Buyer
            HR Manager
            Budget Allocator
        """

        agent1_config = session.get(
            "agent1_config"
        )

        agent2_config = session.get(
            "agent2_config"
        )

        configs = [
            agent1_config,
            agent2_config
        ]

        minimum_roles = {
            "Supplier",
            "Candidate",
            "Budget Requester"
        }

        maximum_roles = {
            "Buyer",
            "HR Manager",
            "Budget Allocator"
        }

        lower_bound = None
        upper_bound = None

        for config in configs:

            if config is None:
                continue

            role = self._get_config_value(
                config,
                "role",
                ""
            )

            reservation_price = (
                self._get_config_value(
                    config,
                    "reservation_price",
                    None
                )
            )

            if reservation_price is None:
                continue

            reservation_price = float(
                reservation_price
            )

            if role in minimum_roles:

                if (
                    lower_bound is None
                    or reservation_price > lower_bound
                ):

                    lower_bound = (
                        reservation_price
                    )

            elif role in maximum_roles:

                if (
                    upper_bound is None
                    or reservation_price < upper_bound
                ):

                    upper_bound = (
                        reservation_price
                    )

        return {
            "lower_bound": lower_bound,
            "upper_bound": upper_bound
        }

    # ============================================================
    # VALIDATE AGREEMENT VALUE
    # ============================================================

    def _is_valid_agreement_value(
        self,
        session,
        value
    ):
        """
        An agreement is valid only when it satisfies BOTH sides'
        configured walk-away boundaries.
        """

        if value is None:
            return False

        boundaries = (
            self._get_agreement_boundaries(
                session
            )
        )

        lower_bound = (
            boundaries.get(
                "lower_bound"
            )
        )

        upper_bound = (
            boundaries.get(
                "upper_bound"
            )
        )

        # No lower boundary configured.
        if (
            lower_bound is not None
            and value < lower_bound
        ):
            return False

        # No upper boundary configured.
        if (
            upper_bound is not None
            and value > upper_bound
        ):
            return False

        return True

    # ============================================================
    # OPPOSITE SPEAKER
    # ============================================================

    def _get_opposite_speaker(
        self,
        scenario,
        speaker
    ):

        pairs = {

            "Vendor Pricing Negotiation": {
                "Buyer": "Supplier",
                "Supplier": "Buyer",
            },

            "Job Offer Negotiation": {
                "Candidate": "HR Manager",
                "HR Manager": "Candidate",
            },

            "Project Budget Allocation": {
                "Budget Requester": "Budget Allocator",
                "Budget Allocator": "Budget Requester",
            }
        }

        return (
            pairs
            .get(
                scenario,
                {}
            )
            .get(
                speaker
            )
        )

    # ============================================================
    # FINAL CONFIRMATION MESSAGE
    # ============================================================

    def _build_final_confirmation(
        self,
        scenario,
        accepting_speaker,
        agreement_value
    ):
        """
        Create a final confirmation from the other participant.
        """

        # ========================================================
        # VENDOR
        # ========================================================

        if scenario == "Vendor Pricing Negotiation":

            if accepting_speaker == "Buyer":

                return (
                    f"We agree to the final price of "
                    f"₹{agreement_value:,.0f} per unit. "
                    f"We confirm the order for 100 units "
                    f"with the agreed terms. "
                    f"The agreement is confirmed."
                )

            return (
                f"We confirm the agreed price of "
                f"₹{agreement_value:,.0f} per unit "
                f"for 100 units. "
                f"We are pleased to finalize the order."
            )

        # ========================================================
        # JOB OFFER
        # ========================================================

        if scenario == "Job Offer Negotiation":

            lpa = (
                agreement_value / 100000
            )

            if accepting_speaker == "Candidate":

                return (
                    f"We agree to the final salary of "
                    f"₹{lpa:g} LPA. "
                    f"We confirm the employment offer "
                    f"on the agreed terms."
                )

            return (
                f"We confirm the agreed salary of "
                f"₹{lpa:g} LPA. "
                f"We are pleased to finalize the offer."
            )

        # ========================================================
        # PROJECT BUDGET
        # ========================================================

        if scenario == "Project Budget Allocation":

            if accepting_speaker == "Budget Requester":

                return (
                    f"We agree to allocate "
                    f"₹{agreement_value:,.0f} "
                    f"to the project. "
                    f"As the Budget Allocator, we confirm "
                    f"that this budget assignment is approved "
                    f"and the agreement is finalized."
                )

            return (
                f"We confirm acceptance of the final budget "
                f"allocation of "
                f"₹{agreement_value:,.0f}. "
                f"We agree to proceed with the project "
                f"at this allocation."
            )

        return (
            "We confirm the agreed terms. "
            "The negotiation is finalized."
        )

    # ============================================================
    # EXPLICIT ACCEPTANCE DETECTION
    # ============================================================

    def _is_explicit_acceptance(
        self,
        message
    ):
        """
        Detect genuine acceptance.

        IMPORTANT:
        Proposal language must NEVER be treated as acceptance.
        """

        if not message:
            return False

        text = " ".join(
            str(message)
            .lower()
            .strip()
            .split()
        )

        # ========================================================
        # PROPOSAL LANGUAGE
        # ========================================================

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
            "we would suggest",

            "can we work with",
            "could we work with",

            "would you work with",

            "can the allocator",
            "could the allocator",

            "can the buyer",
            "could the buyer",

            "can the supplier",
            "could the supplier",

            "can the candidate",
            "could the candidate",

            "can hr",
            "could hr",

            "can we continue",
            "could we continue",

            "let us continue",
            "let's continue",

            "we can continue",
            "we can keep negotiating",
            "we can continue working"
        ]

        if any(
            phrase in text
            for phrase in proposal_phrases
        ):

            return False

        # ========================================================
        # DIRECT ACCEPTANCE
        # ========================================================

        acceptance_phrases = [

            "we accept your offer",
            "i accept your offer",

            "we accept the offer",
            "i accept the offer",

            "we accept your proposal",
            "i accept your proposal",

            "we accept the proposal",
            "i accept the proposal",

            "we happily accept your offer",
            "i happily accept your offer",

            "we gladly accept your offer",
            "i gladly accept your offer",

            "we are happy to accept your offer",
            "i am happy to accept your offer",

            "we are pleased to accept your offer",
            "i am pleased to accept your offer",

            "we agree to your offer",
            "i agree to your offer",

            "we agree to the offer",
            "i agree to the offer",

            "we agree to your proposal",
            "i agree to your proposal",

            "we agree to the proposal",
            "i agree to the proposal",

            "we confirm the agreement",
            "i confirm the agreement",

            "we confirm our agreement",
            "i confirm our agreement",

            "we confirm the deal",
            "i confirm the deal",

            "we confirm our deal",
            "i confirm our deal",

            "we have an agreement",
            "i have an agreement",

            "we have reached an agreement",
            "i have reached an agreement",

            "agreement is confirmed",
            "our agreement is confirmed",

            "the agreement is confirmed",

            "deal is confirmed",
            "the deal is confirmed",

            "deal confirmed"
        ]

        if any(
            phrase in text
            for phrase in acceptance_phrases
        ):

            return True

        # ========================================================
        # STRICT ACCEPTANCE WORD CHECK
        # ========================================================

        if "accept" in text:

            if (
                "offer" in text
                or "proposal" in text
                or "terms" in text
                or "agreement" in text
                or "deal" in text
            ):

                return True

        if "confirmed" in text:

            if (
                "agreement" in text
                or "deal" in text
                or "offer" in text
                or "terms" in text
            ):

                return True

        if (
            "reached"
            in text
            and "agreement"
            in text
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
            if msg.get("speaker")
            in valid_speakers
        ]

        if len(messages) < 8:
            return False

        recent = messages[-6:]

        if len(recent) < 6:
            return False

        normalized = []

        for msg in recent:

            text = (
                str(
                    msg.get(
                        "message",
                        ""
                    )
                )
                .lower()
                .strip()
            )

            normalized.append(
                " ".join(
                    text.split()
                )
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

            text = str(
                msg.get(
                    "message",
                    ""
                )
            ).lower()

            if any(
                phrase in text
                for phrase in deadlock_phrases
            ):

                deadlock_count += 1

        return deadlock_count >= 2

    # ============================================================
    # COMPLETE AGREEMENT
    # ============================================================

    def _complete_agreement(
        self,
        session_id,
        speaker,
        message
    ):

        # ========================================================
        # SYSTEM COMPLETION MESSAGE
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

        session = (
            self.session_manager.get_session(
                session_id
            )
        )

        if session is None:
            return {
                "error": "Invalid session ID"
            }

        valid_speakers = (
            self._get_speaker_names(
                session.get(
                    "scenario"
                )
            )
        )

        turn_count = sum(
            1
            for msg in conversation
            if msg.get("speaker")
            in valid_speakers
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
        # SAVE REPORT
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

        if conversation is None:
            conversation = []

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

        return (
            self.report_generator.generate_report(
                session_id=session_id,
                conversation=conversation,
                status=status,
                scenario=scenario,
                agent1_config=agent1_config,
                agent2_config=agent2_config
            )
        )

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

        report = (
            self.report_generator.generate_report(
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
    # HANDLE ACCEPTANCE
    # ============================================================

    def _handle_ai_acceptance(
        self,
        session_id,
        session,
        conversation,
        ai_speaker,
        ai_reply,
        valid_speakers,
        max_rounds,
        scenario
    ):
        """
        Handle an AI acceptance.

        An explicit acceptance only becomes a real agreement if
        its monetary value is valid for BOTH sides.
        """

        if not self._is_explicit_acceptance(
            ai_reply
        ):

            return None

        # --------------------------------------------------------
        # Try to get the accepted value from the acceptance text.
        # --------------------------------------------------------

        agreement_value = (
            self._extract_last_money_value(
                ai_reply
            )
        )

        # --------------------------------------------------------
        # If the AI says "I accept your offer" without repeating
        # the number, use the latest offer from the other side.
        # --------------------------------------------------------

        if agreement_value is None:

            opposite_speaker = (
                self._get_opposite_speaker(
                    scenario,
                    ai_speaker
                )
            )

            agreement_value = (
                self._get_last_offer_from_speaker(
                    conversation,
                    opposite_speaker
                )
            )

        # --------------------------------------------------------
        # VALID AGREEMENT
        # --------------------------------------------------------

        if (
            agreement_value is not None
            and self._is_valid_agreement_value(
                session,
                agreement_value
            )
        ):

            confirmation_speaker = (
                self._get_opposite_speaker(
                    scenario,
                    ai_speaker
                )
            )

            confirmation_message = (
                self._build_final_confirmation(
                    scenario,
                    ai_speaker,
                    agreement_value
                )
            )

            self.conversation_manager.add_message(
                session_id,
                confirmation_speaker,
                confirmation_message
            )

            return self._complete_agreement(
                session_id,
                confirmation_speaker,
                confirmation_message
            )

        # --------------------------------------------------------
        # INVALID ACCEPTANCE
        # --------------------------------------------------------

        boundaries = (
            self._get_agreement_boundaries(
                session
            )
        )

        lower_bound = (
            boundaries.get(
                "lower_bound"
            )
        )

        upper_bound = (
            boundaries.get(
                "upper_bound"
            )
        )

        self.conversation_manager.add_message(
            session_id,
            "System",
            (
                "The proposed acceptance is outside "
                "the configured negotiation boundaries. "
                "Negotiation will continue."
            )
        )

        turn_count = sum(
            1
            for msg in conversation
            if msg.get("speaker")
            in valid_speakers
        )

        return {
            "session_id": session_id,
            "status": "in_progress",
            "speaker": ai_speaker,
            "message": ai_reply,
            "agreement_valid": False,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "round": turn_count // 2,
            "max_rounds": max_rounds
        }

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

        if session.get(
            "status"
        ) != "in_progress":

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
                self.conversation_manager.get_conversation(
                    session_id
                )
            )

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
            if msg.get(
                "speaker"
            ) in valid_speakers
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
        # REFRESH CONVERSATION
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        # ========================================================
        # EXPLICIT ACCEPTANCE
        # ========================================================

        if self._is_explicit_acceptance(
            ai_reply
        ):

            acceptance_result = (
                self._handle_ai_acceptance(
                    session_id=session_id,
                    session=session,
                    conversation=conversation,
                    ai_speaker=ai_speaker,
                    ai_reply=ai_reply,
                    valid_speakers=valid_speakers,
                    max_rounds=max_rounds,
                    scenario=scenario
                )
            )

            if acceptance_result is not None:

                return acceptance_result

        # ========================================================
        # DEADLOCK
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
        )

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

        turn_count = sum(
            1
            for msg in conversation
            if msg.get("speaker")
            in valid_speakers
        )

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

        if session.get(
            "status"
        ) != "in_progress":

            conversation = (
                self.conversation_manager.get_conversation(
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

        # ========================================================
        # CREATE OPENING
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                session_id
            )
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

        for _ in range(
            max_rounds * 2
        ):

            result = (
                self.simulate_next_turn(
                    session_id
                )
            )

            status = result.get(
                "status"
            )

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
            self.conversation_manager.get_conversation(
                session_id
            )
        )

        # ========================================================
        # SAFETY FALLBACK
        # ========================================================

        if session.get(
            "status"
        ) == "in_progress":

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
                "max_rounds_reached",
                rounds=max_rounds
            )

            self._save_completed_negotiation(
                session_id
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

        if session.get(
            "status"
        ) != "in_progress":

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

        valid_speakers = (
            self._get_speaker_names(
                scenario
            )
        )

        # ========================================================
        # HUMAN AGREEMENT
        # ========================================================

        if self._is_explicit_acceptance(
            request.message
        ):

            agreement_value = (
                self._extract_last_money_value(
                    request.message
                )
            )

            # If the human says "I accept your offer"
            # without repeating the number, use the latest
            # offer made by the opposite participant.

            if agreement_value is None:

                opposite_speaker = (
                    self._get_opposite_speaker(
                        scenario,
                        request.speaker
                    )
                )

                agreement_value = (
                    self._get_last_offer_from_speaker(
                        conversation,
                        opposite_speaker
                    )
                )

            # ----------------------------------------------------
            # VALID AGREEMENT
            # ----------------------------------------------------

            if (
                agreement_value is not None
                and self._is_valid_agreement_value(
                    session,
                    agreement_value
                )
            ):

                confirmation_speaker = (
                    self._get_opposite_speaker(
                        scenario,
                        request.speaker
                    )
                )

                confirmation_message = (
                    self._build_final_confirmation(
                        scenario,
                        request.speaker,
                        agreement_value
                    )
                )

                self.conversation_manager.add_message(
                    request.session_id,
                    confirmation_speaker,
                    confirmation_message
                )

                return self._complete_agreement(
                    request.session_id,
                    confirmation_speaker,
                    confirmation_message
                )

            # ----------------------------------------------------
            # INVALID HUMAN ACCEPTANCE
            # ----------------------------------------------------

            boundaries = (
                self._get_agreement_boundaries(
                    session
                )
            )

            return {
                "session_id": request.session_id,
                "status": "in_progress",
                "speaker": request.speaker,
                "message": request.message,
                "agreement_valid": False,
                "lower_bound": boundaries.get(
                    "lower_bound"
                ),
                "upper_bound": boundaries.get(
                    "upper_bound"
                ),
                "warning": (
                    "The accepted value is outside the "
                    "configured walk-away boundaries. "
                    "Negotiation must continue."
                ),
                "round": (
                    sum(
                        1
                        for message in conversation
                        if message.get(
                            "speaker"
                        ) in valid_speakers
                    )
                    // 2
                ),
                "max_rounds": max_rounds
            }

        # ========================================================
        # DEADLOCK
        # ========================================================

        if self._is_repeated_deadlock(
            conversation,
            valid_speakers
        ):

            self.session_manager.update_status(
                request.session_id,
                "deadlock"
            )

            self._save_completed_negotiation(
                request.session_id
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
        # AI AGREEMENT
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                request.session_id
            )
        )

        if self._is_explicit_acceptance(
            ai_reply
        ):

            acceptance_result = (
                self._handle_ai_acceptance(
                    session_id=request.session_id,
                    session=session,
                    conversation=conversation,
                    ai_speaker=ai_speaker,
                    ai_reply=ai_reply,
                    valid_speakers=valid_speakers,
                    max_rounds=max_rounds,
                    scenario=scenario
                )
            )

            if acceptance_result is not None:

                return acceptance_result

        # ========================================================
        # MAX ROUNDS
        # ========================================================

        conversation = (
            self.conversation_manager.get_conversation(
                request.session_id
            )
        )

        current_round = (
            sum(
                1
                for message in conversation
                if message.get(
                    "speaker"
                ) in valid_speakers
            )
            // 2
        )

        if current_round >= max_rounds:

            self.session_manager.update_status(
                request.session_id,
                "max_rounds_reached",
                rounds=current_round
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

            self._save_completed_negotiation(
                request.session_id
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