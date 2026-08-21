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


class BudgetAgent:

    def __init__(self):

        self.role = "Budget Allocator"

        self.goal = (
            "Protect the organization's available budget while allocating "
            "enough funding for the project to succeed."
        )

        self.constraints = (
            "Do not approve a budget above the available project budget. "
            "Never accept or allocate a value above your configured maximum "
            "acceptable allocation. "
            "If the Budget Requester's demand exceeds your reservation price, "
            "continue negotiating. "
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
                f"Starting target: {starting_target}. "
                f"Maximum acceptable allocation: "
                f"{reservation_price}. "
                f"Never accept or allocate a value above "
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