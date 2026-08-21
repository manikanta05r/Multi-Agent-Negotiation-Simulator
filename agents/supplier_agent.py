from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


def get_config_value(
    config,
    key,
    default=None
):
    """
    Read a configuration value from either a dictionary
    or an object/Pydantic model.
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


class SupplierAgent:

    def __init__(self):

        self.role = "Supplier"

        self.goal = (
            "Sell the product at the highest reasonable price while "
            "reaching a successful agreement."
        )

        self.constraints = (
            "Do not accept an offer below the minimum acceptable price. "
            "Never accept a price below your configured reservation price. "
            "If the buyer's offer is below your minimum acceptable price, "
            "continue negotiating. "
            "Make reasonable concessions when necessary. "
            "Base each counteroffer on the buyer's latest offer. "
            "Do not repeat the same price multiple times. "
            "Be polite and professional. "
            "If the buyer reaches a fair final price within your acceptable "
            "range, accept explicitly."
        )

    def negotiate(
        self,
        conversation_history,
        scenario,
        agent_config=None
    ):

        dynamic_constraints = self.constraints

        if agent_config:

            strategy = get_config_value(
                agent_config,
                "strategy"
            )

            starting_target = get_config_value(
                agent_config,
                "starting_target"
            )

            reservation_price = get_config_value(
                agent_config,
                "reservation_price"
            )

            instructions = get_config_value(
                agent_config,
                "instructions"
            )

            dynamic_constraints += (
                f" Negotiation strategy: {strategy}. "
                f"Starting target price: {starting_target}. "
                f"Minimum acceptable price: {reservation_price}. "
                f"Never accept a price below "
                f"{reservation_price}. "
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

        response = generate_response(
            prompt
        )

        return parse_response(
            response
        )