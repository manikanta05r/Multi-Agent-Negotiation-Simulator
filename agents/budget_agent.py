from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class BudgetAgent:

    def __init__(self):
        self.role = "Budget Allocator"

        self.goal = (
            "Protect the organization's available budget while allocating "
            "enough funding for the project to succeed."
        )

        self.constraints = (
            "Do not approve a budget above the available project budget. "
            "Evaluate each request against the project's needs. "
            "Make reasonable counteroffers rather than rejecting proposals "
            "without explanation. "
            "Be professional and financially responsible. "
            "Do not repeat the same counteroffer multiple times. "
            "Do not introduce unrelated topics. "
            "Always refer to yourself as the Budget Allocator."
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
                f"Starting target: {starting_target}. "
                f"Maximum acceptable allocation: {reservation_price}. "
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