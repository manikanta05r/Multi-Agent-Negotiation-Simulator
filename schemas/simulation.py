from pydantic import BaseModel


class SimulationRequest(BaseModel):
    session_id: str