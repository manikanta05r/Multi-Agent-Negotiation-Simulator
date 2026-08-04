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

    def negotiate(self, conversation_history, scenario):

        prompt = build_prompt(
            role=self.role,
            goal=self.goal,
            constraints=self.constraints,
            scenario=scenario,
            conversation_history=conversation_history
        )

        response = generate_response(prompt)

        return parse_response(response)