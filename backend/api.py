from fastapi import FastAPI

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