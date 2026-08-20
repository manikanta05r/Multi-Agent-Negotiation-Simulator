from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class SupplierAgent:

    def __init__(self):

        self.role = "Supplier"

        self.goal = (
            "Sell the product at the highest reasonable price while "
            "reaching a successful agreement."
        )

        self.constraints = (
            "Do not accept an offer below the minimum acceptable price. "
            "Make reasonable concessions when necessary. "
            "Base each counteroffer on the buyer's latest offer. "
            "Do not repeat the same price multiple times. "
            "Be polite and professional. "
            "If the buyer reaches a fair final price, accept explicitly."
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
                f"Starting target price: {starting_target}. "
                f"Minimum acceptable price: {reservation_price}. "
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