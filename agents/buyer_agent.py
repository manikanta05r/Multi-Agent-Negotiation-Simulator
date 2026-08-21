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


class BuyerAgent:

    def __init__(self):

        self.role = "Buyer"

        self.goal = (
            "Buy the product at the lowest reasonable price while "
            "reaching a successful agreement."
        )

        self.constraints = (
            "Stay within the available budget. "
            "Never accept a price above your configured maximum "
            "acceptable price. "
            "If the supplier's offer exceeds your reservation price, "
            "continue negotiating. "
            "Negotiate politely for a better price. "
            "Make reasonable counteroffers based on the supplier's "
            "latest offer. "
            "Do not make the same counteroffer repeatedly. "
            "Do not immediately accept unless the offer is fair "
            "and within the acceptable range. "
            "If the supplier reaches a reasonable final price within "
            "your acceptable range, accept the offer explicitly. "
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
                f"Maximum acceptable price: {reservation_price}. "
                f"Never accept a price above "
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