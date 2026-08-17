from typing import Dict, Any
from pydantic import BaseModel


class AgentConfig(BaseModel):
    name: str
    role: str
    strategy: str
    starting_target: float
    reservation_price: float
    instructions: str = ""


class NegotiationRequest(BaseModel):
    scenario: str
    mode: str
    max_rounds: int

    project_total_budget: float | None = None

    agent1_config: AgentConfig | None = None
    agent2_config: AgentConfig | None = None


class NegotiationResponse(BaseModel):
    status: str
    message: str