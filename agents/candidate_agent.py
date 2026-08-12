from llm.gemini_client import generate_response
from llm.prompt_builder import build_prompt
from llm.response_parser import parse_response


class CandidateAgent:

    def __init__(self):
        self.role = "Candidate"

        self.goal = (
            "Secure the best possible salary while remaining professional and reaching a mutually acceptable agreement."
        )

        self.constraints = (
            "Negotiate professionally to obtain the best possible salary and benefits. "
            "Do not accept the first offer immediately unless it already meets your expectations. "
            "Make reasonable counteroffers during the negotiation. "
            "If the employer reaches a fair final offer close to your latest expectation, accept the offer. "
            "Do not repeat the same counteroffer multiple times. "
            "Do not introduce new topics that were not already discussed."
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