from pydantic import BaseModel


class NextRoundRequest(BaseModel):
    session_id: str
    speaker: str
    message: str


class NextRoundResponse(BaseModel):
    session_id: str
    speaker: str
    message: str