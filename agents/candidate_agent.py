from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class CandidateAgent:

    def __init__(self):

        self.role = "Candidate"

        self.goal = (
            "Secure the best possible salary while remaining professional "
            "and reaching a mutually acceptable agreement."
        )

        self.constraints = (
            "Negotiate professionally for the best possible salary. "
            "Make reasonable counteroffers based on the HR Manager's "
            "latest offer. "
            "Do not accept the first offer immediately unless it already "
            "meets expectations. "
            "Do not repeat the same salary request multiple times. "
            "If the employer reaches a fair final offer close to the "
            "candidate's acceptable range, accept explicitly. "
            "Do not introduce unrelated topics."
        )

    def negotiate(
        self,
        conversation_history,
        scenario,
        agent_config=None
    ):

        dynamic_constraints = self.constraints

        if agent_config:

            strategy = getattr(
                agent_config,
                "strategy",
                None
            )

            starting_target = getattr(
                agent_config,
                "starting_target",
                None
            )

            reservation_price = getattr(
                agent_config,
                "reservation_price",
                None
            )

            instructions = getattr(
                agent_config,
                "instructions",
                None
            )

            dynamic_constraints += (
                f" Negotiation strategy: {strategy}. "
                f"Starting salary target: {starting_target}. "
                f"Minimum acceptable salary: {reservation_price}. "
                f"Custom instructions: {instructions}."
            )

        prompt = build_prompt(
            role=self.role,
            goal=self.goal,
            constraints=dynamic_constraints,
            scenario=scenario,
            conversation_history=conversation_history,
            agent_config=agent_config
        )

        response = generate_response(prompt)

        return parse_response(response)