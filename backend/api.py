from fastapi import FastAPI
from schemas.next_round import NextRoundRequest
from schemas.simulation import SimulationRequest
from schemas.negotiation import NegotiationRequest
from backend.orchestrator import NegotiationOrchestrator

app = FastAPI(
    title="Multi-Agent Negotiation Simulator API",
    version="1.0.0"
)

orchestrator = NegotiationOrchestrator()


@app.get("/")
def home():
    return {"message": "Backend Running"}


@app.get("/health")
def health():
    return {"status": "Healthy"}


@app.post("/start-negotiation")
def start_negotiation(request: NegotiationRequest):
    return orchestrator.start(request)

@app.post("/next-round")
def next_round(request: NextRoundRequest):
    return orchestrator.next_round(request)

@app.post("/simulate-negotiation")
def simulate_negotiation(request: SimulationRequest):
    return orchestrator.simulate_negotiation(request.session_id)

@app.get("/conversation/{session_id}")
def get_conversation(session_id: str):
    return orchestrator.conversation_manager.get_conversation(session_id)

@app.get("/report/{session_id}")
def get_report(session_id: str):
    return orchestrator.generate_report(session_id)