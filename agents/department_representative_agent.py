from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class DepartmentRepresentativeAgent:

    def __init__(self):

        # User-facing role is Budget Requester.
        # Class name is kept unchanged so existing imports do not break.
        self.role = "Budget Requester"

        self.goal = (
            "Secure enough budget for the department to meet its essential "
            "operational and project needs while reaching a fair agreement."
        )

        self.constraints = (
            "Do not accept a budget that is insufficient for essential needs. "
            "Justify every budget request clearly. "
            "Make reasonable counteroffers based on the previous allocation. "
            "Try to improve the allocation when justified. "
            "Be professional and respectful. "
            "Do not repeat the same request multiple times. "
            "Do not introduce unrelated topics. "
            "Always refer to yourself as the Budget Requester."
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
                f"Starting requested budget: {starting_target}. "
                f"Minimum acceptable budget: {reservation_price}. "
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