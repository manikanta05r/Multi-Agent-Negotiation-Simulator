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


class DepartmentRepresentativeAgent:

    def __init__(self):

        # User-facing role.
        self.role = "Budget Requester"

        self.goal = (
            "Secure enough budget for the department to meet its essential "
            "operational and project needs while reaching a fair agreement."
        )

        self.constraints = (
            "Do not accept a budget that is insufficient for essential needs. "
            "Never accept a budget below your configured minimum acceptable "
            "budget. "
            "If the allocator's offer is below your walk-away boundary, "
            "continue negotiating. "
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
                f"Starting requested budget: {starting_target}. "
                f"Minimum acceptable budget: {reservation_price}. "
                f"Never accept a budget below "
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