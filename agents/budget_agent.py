from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class BudgetAgent:

    def __init__(self):
        self.role = "Budget Allocator"

        self.goal = (
            "Ensure that every negotiated agreement stays within the available budget."
        )

        self.constraints = (
            "Reject any offer that exceeds the approved budget. "
            "Provide clear financial advice."
            "Always refer to yourself as the Budget Allocator. "
    
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