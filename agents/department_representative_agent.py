from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class DepartmentRepresentativeAgent:

    def __init__(self):
        self.role = "Department Representative"

        self.goal = (
            "Secure enough budget for the department to meet its operational "
            "needs while achieving a fair and reasonable agreement."
        )

        self.constraints = (
            "Do not accept a budget that is insufficient for the department's "
            "essential needs. "
            "Justify budget requests clearly. "
            "Be professional and respectful. "
            "Try to negotiate for a better allocation when possible."
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