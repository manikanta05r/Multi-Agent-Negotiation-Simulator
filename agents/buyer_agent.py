from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class BuyerAgent:

    def __init__(self):
        self.role = "Buyer"

        self.goal = (
            "Buy the product at the lowest possible price."
        )

        self.constraints = (
            "Never exceed the budget. "
            "Be polite. "
            "Always try to negotiate a lower price."
        )

    def negotiate(self, conversation_history):

        prompt = build_prompt(
            role=self.role,
            goal=self.goal,
            constraints=self.constraints,
            conversation_history=conversation_history
        )

        response = generate_response(prompt)

        return parse_response(response)