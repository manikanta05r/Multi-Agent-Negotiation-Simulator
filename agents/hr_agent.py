from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class HRAgent:

    def __init__(self):
        self.role = "HR Manager"

        self.goal = (
            "Hire the best candidate while staying within the company's salary budget."
        )

        self.constraints = (
            "Do not exceed the approved salary budget. "
            "Be professional and respectful."
        )

    def negotiate(
            self,
            conversation_history,
            scenario,
            agent_config=None
        ):

        prompt = build_prompt(
            role=self.role,
            goal=self.goal,
            constraints=self.constraints,
            scenario=scenario,
            conversation_history=conversation_history,
            agent_config=agent_config
        )

        response = generate_response(prompt)

        return parse_response(response)