from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class BudgetAgent:

    def __init__(self):
        self.role = "Budget Advisor"

        self.goal = (
            "Ensure that every negotiated agreement stays within the available budget."
        )

        self.constraints = (
            "Reject any offer that exceeds the approved budget. "
            "Provide clear financial advice."
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