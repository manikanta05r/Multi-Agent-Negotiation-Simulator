from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class SupplierAgent:

    def __init__(self):
        self.role = "Supplier"

        self.goal = (
            "Sell the product at the highest possible price while reaching a successful deal."
        )

        self.constraints = (
            "Do not accept an offer below the minimum acceptable price. "
            "Be polite and professional. "
            "Always try to negotiate a better price."
        )

    def negotiate(
        self,
        conversation_history,
        scenario,
        agent_config=None
    ):

        if agent_config:

            strategy = agent_config.strategy

            starting_target = agent_config.starting_target

            reservation_price = agent_config.reservation_price

            instructions = agent_config.instructions

            dynamic_constraints = (
                f"Negotiation strategy: {strategy}. "
                f"Starting target: {starting_target}. "
                f"Reservation price / walk-away: {reservation_price}. "
                f"Custom instructions: {instructions}"
            )

        else:

            dynamic_constraints = self.constraints

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