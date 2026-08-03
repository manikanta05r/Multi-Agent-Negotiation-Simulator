from pydantic import BaseModel


class NegotiationRequest(BaseModel):
    scenario: str
    mode: str
    max_rounds: int


class NegotiationResponse(BaseModel):
    status: str
    message: str