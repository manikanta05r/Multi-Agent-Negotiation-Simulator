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


class CandidateAgent:

    def __init__(self):

        self.role = "Candidate"

        self.goal = (
            "Secure the best possible salary while remaining professional "
            "and reaching a mutually acceptable agreement."
        )

        self.constraints = (
            "Negotiate professionally for the best possible salary. "
            "Never accept a salary below your configured minimum "
            "acceptable salary. "
            "If HR's offer is below your reservation salary, "
            "continue negotiating. "
            "Make reasonable counteroffers based on the HR Manager's "
            "latest offer. "
            "Do not accept the first offer immediately unless it already "
            "meets the configured acceptable range. "
            "Do not repeat the same salary request multiple times. "
            "If the employer reaches a fair final offer within the "
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
                f"Starting salary target: {starting_target}. "
                f"Minimum acceptable salary: {reservation_price}. "
                f"Never accept a salary below "
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