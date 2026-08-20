from fastapi import FastAPI

from schemas.next_round import NextRoundRequest
from schemas.simulation import SimulationRequest
from schemas.negotiation import NegotiationRequest

from backend.orchestrator import NegotiationOrchestrator


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Multi-Agent Negotiation Simulator API",
    version="1.0.0",
)


# ============================================================
# ORCHESTRATOR
# ============================================================

orchestrator = NegotiationOrchestrator()


# ============================================================
# SCENARIO AGENTS
# ============================================================

SCENARIO_AGENTS = {

    "Vendor Pricing Negotiation": {
        "agent1": "Buyer",
        "agent2": "Supplier",
    },

    "Job Offer Negotiation": {
        "agent1": "Candidate",
        "agent2": "HR Manager",
    },

    "Project Budget Allocation": {
        "agent1": "Budget Requester",
        "agent2": "Budget Allocator",
    },
}


# ============================================================
# SPEAKER ALIASES
#
# Existing implementation class:
#
# department_representative_agent.py
#
# User-facing name:
#
# Budget Requester
# ============================================================

SPEAKER_ALIASES = {
    "Department Representative": "Budget Requester",
    "department representative": "Budget Requester",
}


# ============================================================
# HELPERS
# ============================================================

def get_scenario_agents(scenario):

    return SCENARIO_AGENTS.get(
        scenario,
        {
            "agent1": "Agent 1",
            "agent2": "Agent 2",
        },
    )


def normalize_speaker(speaker):

    if not speaker:
        return speaker

    return SPEAKER_ALIASES.get(
        speaker,
        speaker,
    )


def normalize_conversation(conversation):

    if not conversation:
        return []

    normalized = []

    for message in conversation:

        if not isinstance(message, dict):
            normalized.append(message)
            continue

        message_copy = dict(message)

        message_copy["speaker"] = normalize_speaker(
            message_copy.get("speaker")
        )

        normalized.append(
            message_copy
        )

    return normalized


def get_negotiation_messages(
    conversation,
    agents,
):

    if not conversation:
        return []

    valid_speakers = {
        agents["agent1"],
        agents["agent2"],
    }

    return [
        message
        for message in conversation
        if message.get("speaker")
        in valid_speakers
    ]


# ============================================================
# ROUND CALCULATION
# ============================================================
#
# IMPORTANT:
#
# The first message is the opening offer.
#
# We DO NOT consider that a completed round.
#
# Examples:
#
# 0 messages -> Round 0
# 1 message  -> Round 0
# 2 messages -> Round 1
# 3 messages -> Round 1
# 4 messages -> Round 2
# 5 messages -> Round 2
#
# This matches the orchestrator:
#
# completed_rounds = turn_count // 2
#
# ============================================================

def calculate_round(message_count):

    if message_count <= 0:
        return 0

    return message_count // 2


# ============================================================
# NEXT AGENT
# ============================================================
#
# STRICT ZIG-ZAG
#
# 0 messages -> Agent 1
# 1 message  -> Agent 2
# 2 messages -> Agent 1
# 3 messages -> Agent 2
# 4 messages -> Agent 1
#
# ============================================================

def get_next_agent(
    message_count,
    agents,
):

    if message_count % 2 == 0:
        return agents["agent1"]

    return agents["agent2"]


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Backend Running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "Healthy"
    }


# ============================================================
# START NEGOTIATION
# ============================================================

@app.post("/start-negotiation")
def start_negotiation(
    request: NegotiationRequest
):

    return orchestrator.start(
        request
    )


# ============================================================
# NEXT ROUND
# ============================================================

@app.post("/next-round")
def next_round(
    request: NextRoundRequest
):

    return orchestrator.next_round(
        request
    )


# ============================================================
# FULL SIMULATION
# ============================================================

@app.post("/simulate-negotiation")
def simulate_negotiation(
    request: SimulationRequest
):

    return orchestrator.simulate_negotiation(
        request.session_id
    )


# ============================================================
# ONE AI TURN
# ============================================================

@app.post("/simulate-next-turn")
def simulate_next_turn(
    request: SimulationRequest
):

    """
    Generate exactly ONE AI turn.

    The frontend repeatedly calls this endpoint.

    The orchestrator is responsible for deciding
    which agent speaks next.

    Example:

        Opening:
            Budget Requester
                  ↓
            Budget Allocator
                  ↓
            Budget Requester
                  ↓
            Budget Allocator
                  ↓
                  ...

    """

    return orchestrator.simulate_next_turn(
        request.session_id
    )


# ============================================================
# GET NEGOTIATION STATE
# ============================================================

@app.get("/negotiation/{session_id}")
def get_negotiation(
    session_id: str
):

    # ========================================================
    # GET SESSION
    # ========================================================

    session = (
        orchestrator
        .session_manager
        .get_session(
            session_id
        )
    )

    if session is None:

        return {
            "error": "Invalid session ID"
        }


    # ========================================================
    # GET RAW CONVERSATION
    # ========================================================

    raw_conversation = (
        orchestrator
        .conversation_manager
        .get_conversation(
            session_id
        )
    )

    if raw_conversation is None:
        raw_conversation = []


    # ========================================================
    # NORMALIZE SPEAKERS
    # ========================================================

    conversation = normalize_conversation(
        raw_conversation
    )


    # ========================================================
    # SESSION DATA
    # ========================================================

    status = session.get(
        "status",
        "in_progress",
    )

    scenario = session.get(
        "scenario",
        "",
    )

    max_rounds = session.get(
        "max_rounds",
        10,
    )


    # ========================================================
    # AGENTS
    # ========================================================

    agents = get_scenario_agents(
        scenario
    )

    agent1 = agents["agent1"]
    agent2 = agents["agent2"]


    # ========================================================
    # NEGOTIATION MESSAGES
    # ========================================================

    negotiation_messages = (
        get_negotiation_messages(
            conversation,
            agents,
        )
    )

    message_count = len(
        negotiation_messages
    )


    # ========================================================
    # ROUND
    # ========================================================

    rounds = calculate_round(
        message_count
    )


    # ========================================================
    # MAX ROUND
    # ========================================================
    #
    # Do NOT override an already completed state.
    #
    # Only mark the session as maximum-rounds-reached
    # when the backend session is still in progress.
    #
    # ========================================================

    if (
        status == "in_progress"
        and rounds >= max_rounds
        and message_count >= 2
    ):

        status = "max_rounds_reached"

        orchestrator.session_manager.update_status(
            session_id,
            "max_rounds_reached"
        )


    # ========================================================
    # ACTIVE AGENT
    # ========================================================

    active_agent = None

    if status == "in_progress":

        active_agent = get_next_agent(
            message_count,
            agents,
        )


    # ========================================================
    # LAST SPEAKER
    # ========================================================

    last_speaker = None

    if negotiation_messages:

        last_speaker = normalize_speaker(
            negotiation_messages[-1].get(
                "speaker"
            )
        )


    # ========================================================
    # NEXT SPEAKER
    # ========================================================

    next_speaker = None

    if status == "in_progress":

        next_speaker = active_agent


    # ========================================================
    # RETURN STATE
    # ========================================================

    return {

        "session_id": session_id,

        "scenario": scenario,

        "mode": session.get(
            "mode"
        ),

        "status": status,

        "round": rounds,

        "max_rounds": max_rounds,

        "active_agent": active_agent,

        "next_speaker": next_speaker,

        "last_speaker": last_speaker,

        "agent1": agent1,

        "agent2": agent2,

        "message_count": message_count,

        "messages": conversation,
    }


# ============================================================
# CONVERSATION
# ============================================================

@app.get("/conversation/{session_id}")
def get_conversation(
    session_id: str
):

    conversation = (
        orchestrator
        .conversation_manager
        .get_conversation(
            session_id
        )
    )

    return normalize_conversation(
        conversation or []
    )


# ============================================================
# REPORT
# ============================================================

@app.get("/report/{session_id}")
def get_report(
    session_id: str
):

    return orchestrator.generate_report(
        session_id
    )