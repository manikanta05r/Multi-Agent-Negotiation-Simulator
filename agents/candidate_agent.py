from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class CandidateAgent:

    def __init__(self):
        self.role = "Candidate"

        self.goal = (
            "Secure the best possible salary and benefits while remaining professional."
        )

        self.constraints = (
            "Do not accept an offer below your expected salary. "
            "Be polite and professional."
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