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


class HRAgent:

    def __init__(self):

        self.role = "HR Manager"

        self.goal = (
            "Hire the best candidate while staying within the company's "
            "approved salary budget and reaching a fair agreement."
        )

        self.constraints = (
            "Do not exceed the approved salary budget. "
            "Never accept or offer a salary above your configured "
            "maximum approved salary. "
            "If the candidate's request exceeds your reservation price, "
            "continue negotiating. "
            "Make reasonable salary counteroffers based on the candidate's "
            "latest request. "
            "Do not repeat the same salary offer multiple times. "
            "Be professional and respectful. "
            "Do not introduce unrelated topics. "
            "If the candidate's request reaches a fair and affordable "
            "level within your acceptable range, accept explicitly."
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
                f"Starting salary offer: {starting_target}. "
                f"Maximum approved salary: {reservation_price}. "
                f"Never accept or offer a salary above "
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