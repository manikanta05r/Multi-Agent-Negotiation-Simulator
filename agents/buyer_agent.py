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
            "Stay within the available budget. "
            "Negotiate politely for a better price. "
            "Make reasonable counteroffers. "
            "If the supplier reaches a fair final price within your acceptable budget, accept the offer. "
            "Do not repeat the same counteroffer multiple times. "
            "Do not introduce unrelated topics."
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