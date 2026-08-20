from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class HRAgent:

    def __init__(self):

        self.role = "HR Manager"

        self.goal = (
            "Hire the best candidate while staying within the company's "
            "approved salary budget and reaching a fair agreement."
        )

        self.constraints = (
            "Do not exceed the approved salary budget. "
            "Make reasonable salary counteroffers based on the candidate's "
            "latest request. "
            "Do not repeat the same salary offer multiple times. "
            "Be professional and respectful. "
            "Do not introduce unrelated topics. "
            "If the candidate's request reaches a fair and affordable "
            "level, accept explicitly."
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
                f"Starting salary offer: {starting_target}. "
                f"Maximum approved salary: {reservation_price}. "
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