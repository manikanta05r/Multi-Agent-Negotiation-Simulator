import re

from llm.summary_generator import generate_summary




def extract_negotiation_values(message):
    """
    Extract monetary negotiation values from a message.

    Examples:
    ₹95,000
    ₹1,00,000
    95000 rupees
    95,000 rupees
    """

    if not message:
        return []

    values = []

    patterns = [
        r"₹\s*([\d,]+(?:\.\d+)?)",
        r"([\d,]+(?:\.\d+)?)\s*(?:rupees|INR)",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            message,
            flags=re.IGNORECASE
        )

        for value in matches:

            try:

                value = float(
                    value.replace(",", "")
                )

                values.append(value)

            except ValueError:
                continue

    return values



def extract_primary_offer(message):
    """
    Extract the most likely actual offer made by the speaker.

    The final monetary value in a negotiation message is usually
    the speaker's current offer or concession.
    """

    values = extract_negotiation_values(message)

    if not values:
        return None

    return values[-1]


def calculate_boundary_score(
    conversation,
    agent1_config=None,
    agent2_config=None
):
    """
    Evaluate whether agents stayed within
    their configured negotiation boundaries.

    Maximum score: 10
    """

    configured_agents = [
        agent1_config,
        agent2_config
    ]

    configured_agents = [
        config
        for config in configured_agents
        if config is not None
    ]

    if not configured_agents:
        return 0

    valid_agents = 0
    boundary_violations = 0

    for config in configured_agents:

        role = getattr(
            config,
            "role",
            ""
        )

        reservation_price = getattr(
            config,
            "reservation_price",
            None
        )

        if reservation_price is None:
            continue

        valid_agents += 1

        for message in conversation:

            speaker = message.get(
                "speaker",
                ""
            )

            # Only evaluate messages belonging
            # to this configured agent role.
            if speaker != role:
                continue

            value = extract_primary_offer(
                message.get("message", "")
            )

            if value is None:
                continue

            # Buyer / HR Manager / Budget Allocator:
            # normally should not go above
            # their reservation price.
            if role in [
                "Buyer",
                "HR Manager",
                "Budget Allocator"
            ]:

                if value > reservation_price:
                    boundary_violations += 1

            # Supplier / Candidate / Budget Requester:
            # normally should not go below
            # their reservation price.
            elif role in [
                "Supplier",
                "Candidate",
                "Budget Requester"
            ]:

                if value < reservation_price:
                    boundary_violations += 1

    if valid_agents == 0:
        return 0

    if boundary_violations == 0:
        return 10

    if boundary_violations == 1:
        return 5

    return 0
def calculate_concession_score(
    conversation,
    agent1_config=None,
    agent2_config=None
):
    """
    Evaluate how effectively agents make concessions.

    Maximum score: 15

    5 points  - Meaningful concessions are made
    5 points  - Concessions are gradual and reasonable
    5 points  - Agents avoid unnecessary or repeated offers
    """

    configured_agents = [
        agent1_config,
        agent2_config
    ]

    configured_agents = [
        config
        for config in configured_agents
        if config is not None
    ]

    if not configured_agents:
        return 0

    # ------------------------------------------
    # Collect offers made by each agent
    # ------------------------------------------

    agent_offers = {}

    for config in configured_agents:

        role = getattr(
            config,
            "role",
            ""
        )

        agent_offers[role] = []

        for message in conversation:

            if message.get("speaker") != role:
                continue

            values = extract_negotiation_values(
                message.get("message", "")
            )

            if values:

                agent_offers[role].extend(
                    values
                )

    # ------------------------------------------
    # No numerical offers
    # ------------------------------------------

    if not any(agent_offers.values()):
        return 0

    meaningful_concessions = 0
    gradual_concessions = 0
    repeated_offers = 0

    # ------------------------------------------
    # Analyze each agent's offers
    # ------------------------------------------

    for role, offers in agent_offers.items():

        if len(offers) < 2:
            continue

        previous_offer = None

        for offer in offers:

            if previous_offer is None:
                previous_offer = offer
                continue

            # Same offer repeated
            if offer == previous_offer:

                repeated_offers += 1

                previous_offer = offer

                continue

            # Any numerical movement
            meaningful_concessions += 1

            difference = abs(
                offer - previous_offer
            )

            # Calculate percentage movement
            percentage_change = (
                difference / previous_offer * 100
                if previous_offer != 0
                else 0
            )

            # A reasonable concession is
            # between 0% and 10%.
            if 0 < percentage_change <= 10:

                gradual_concessions += 1

            previous_offer = offer

    # ------------------------------------------
    # SCORE 1 — Meaningful concessions
    # ------------------------------------------

    concession_score = 0

    if meaningful_concessions >= 1:
        concession_score += 5

    # ------------------------------------------
    # SCORE 2 — Gradual concessions
    # ------------------------------------------

    if gradual_concessions >= 1:
        concession_score += 5

    # ------------------------------------------
    # SCORE 3 — Avoid repeated offers
    # ------------------------------------------

    if repeated_offers == 0:
        concession_score += 5

    elif repeated_offers == 1:
        concession_score += 2

    return min(
        concession_score,
        15
    )

def calculate_score_breakdown(
    conversation,
    status,
    agent1_config=None,
    agent2_config=None
):

    # ======================================================
    # 1. OUTCOME SCORE — 30 POINTS
    # ======================================================

    if status == "agreement_reached":
        outcome_score = 30

    elif status == "deadlock":
        outcome_score = 15

    elif status == "max_rounds_reached":
        outcome_score = 10

    else:
        outcome_score = 0


    # ======================================================
    # 2. DEAL QUALITY — 25 POINTS
    # ======================================================

    if status == "agreement_reached":
        deal_quality_score = 25

    elif status == "deadlock":
        deal_quality_score = 10

    elif status == "max_rounds_reached":
        deal_quality_score = 5

    else:
        deal_quality_score = 0


    # ======================================================
    # 3. STRATEGY ADHERENCE — 20 POINTS
    # ======================================================

    configured_agents = [
        agent1_config,
        agent2_config
    ]

    configured_agents = [
        config
        for config in configured_agents
        if config is not None
    ]

    strategy_score = 0

    if configured_agents:

        valid_strategies = {
            "Collaborative",
            "Competitive",
            "Assertive",
            "Compromising",
            "Flexible"
        }

        valid_strategy_count = sum(
            1
            for config in configured_agents
            if getattr(config, "strategy", None)
            in valid_strategies
        )

        if valid_strategy_count == len(configured_agents):
            strategy_score = 20

        elif valid_strategy_count > 0:
            strategy_score = 10


    # ======================================================
    # 4. CONCESSION EFFICIENCY — 15 POINTS
    # ======================================================

    concession_score = calculate_concession_score(
        conversation,
        agent1_config,
        agent2_config
    )

    # ======================================================
    # 5. BOUNDARY MANAGEMENT — 10 POINTS
    # ======================================================

    boundary_score = calculate_boundary_score(
        conversation,
        agent1_config,
        agent2_config
    )

    # ======================================================
    # FINAL SCORE
    # ======================================================

    total_score = (
        outcome_score
        + deal_quality_score
        + strategy_score
        + concession_score
        + boundary_score
    )

    total_score = min(
        total_score,
        100
    )


    return {
        "outcome": outcome_score,
        "deal_quality": deal_quality_score,
        "strategy_adherence": strategy_score,
        "concession_efficiency": concession_score,
        "boundary_management": boundary_score,
        "total": total_score
    }



def calculate_negotiation_score(
    conversation,
    status,
    agent1_config=None,
    agent2_config=None
):

    breakdown = calculate_score_breakdown(
        conversation,
        status,
        agent1_config,
        agent2_config
    )

    return breakdown["total"]


class ReportGenerator:

    def generate_report(
        self,
        session_id,
        conversation,
        status,
        scenario,
        agent1_config=None,
        agent2_config=None
    ):

        participants = list(
            {
                msg["speaker"]
                for msg in conversation
            }
        )

        negotiation_speakers = [
            "Buyer",
            "Supplier",
            "Candidate",
            "HR Manager",
            "Budget Requester",
            "Budget Allocator"
        ]

        turn_count = sum(
            1
            for msg in conversation
            if msg["speaker"] in negotiation_speakers
        )

        total_rounds = turn_count // 2

        try:
            summary = generate_summary(
                conversation,
                scenario,
                status
            )

        except Exception as e:
            print("Summary Error:", e)

            summary = "AI summary could not be generated."

        negotiation_score = calculate_negotiation_score(
            conversation,
            status,
            agent1_config,
            agent2_config
        )

        score_breakdown = calculate_score_breakdown(
            conversation,
            status,
            agent1_config,
            agent2_config
        )

        report = {
            "session_id": session_id,
            "scenario": scenario,
            "status": status,
            "total_rounds": total_rounds,
            "participants": participants,
            "negotiation_score": negotiation_score,
            "score_breakdown": score_breakdown,
            "summary": summary,
            "conversation": conversation
        }

        return report

