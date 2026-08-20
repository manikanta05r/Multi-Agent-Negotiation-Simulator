from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class BuyerAgent:

    def __init__(self):

        self.role = "Buyer"

        self.goal = (
            "Buy the product at the lowest reasonable price while "
            "reaching a successful agreement."
        )

        self.constraints = (
            "Stay within the available budget. "
            "Negotiate politely for a better price. "
            "Make reasonable counteroffers based on the supplier's "
            "latest offer. "
            "Do not make the same counteroffer repeatedly. "
            "Do not immediately accept unless the offer is fair "
            "and within the acceptable range. "
            "If the supplier reaches a reasonable final price, "
            "accept the offer explicitly. "
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
                f"Starting target price: {starting_target}. "
                f"Maximum acceptable price: {reservation_price}. "
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