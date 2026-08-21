import re

from llm.summary_generator import generate_summary


# ============================================================
# CONFIG VALUE HELPER
# ============================================================

def get_config_value(
    config,
    key,
    default=None
):
    """
    Read a configuration value from either:

    - a Pydantic/object-style AgentConfig
    - a dictionary loaded from storage

    This keeps the scoring logic compatible with both.
    """

    if config is None:
        return default

    if isinstance(config, dict):
        return config.get(
            key,
            default
        )

    return getattr(
        config,
        key,
        default
    )


# ============================================================
# MONEY EXTRACTION
# ============================================================

def extract_negotiation_values(message):
    """
    Extract monetary negotiation values from a message.

    Examples:
        ₹95,000
        ₹1,00,000
        ₹95000
        95000 rupees
        95,000 rupees
        95000 INR
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
            str(message),
            flags=re.IGNORECASE
        )

        for value in matches:

            try:
                numeric_value = float(
                    value.replace(",", "")
                )

                values.append(
                    numeric_value
                )

            except (
                TypeError,
                ValueError
            ):
                continue

    return values


# ============================================================
# PRIMARY OFFER
# ============================================================

def extract_primary_offer(message):
    """
    Extract the most likely current offer from a message.

    The final monetary value mentioned by the speaker
    is treated as the speaker's current position.
    """

    values = extract_negotiation_values(
        message
    )

    if not values:
        return None

    return values[-1]


# ============================================================
# BOUNDARY SCORE
# ============================================================

def calculate_boundary_score(
    conversation,
    agent1_config=None,
    agent2_config=None
):
    """
    Evaluate whether agents stayed within their
    configured reservation boundaries.

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

        role = get_config_value(
            config,
            "role",
            ""
        )

        reservation_price = get_config_value(
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

            if speaker != role:
                continue

            value = extract_primary_offer(
                message.get(
                    "message",
                    ""
                )
            )

            if value is None:
                continue

            # ------------------------------------------------
            # BUY-SIDE / MAXIMUM LIMIT
            # ------------------------------------------------

            if role in [
                "Buyer",
                "HR Manager",
                "Budget Allocator"
            ]:

                if value > float(
                    reservation_price
                ):
                    boundary_violations += 1

            # ------------------------------------------------
            # SELL-SIDE / MINIMUM LIMIT
            # ------------------------------------------------

            elif role in [
                "Supplier",
                "Candidate",
                "Budget Requester"
            ]:

                if value < float(
                    reservation_price
                ):
                    boundary_violations += 1

    if valid_agents == 0:
        return 0

    if boundary_violations == 0:
        return 10

    if boundary_violations == 1:
        return 5

    return 0


# ============================================================
# CONCESSION SCORE
# ============================================================

def calculate_concession_score(
    conversation,
    agent1_config=None,
    agent2_config=None
):
    """
    Evaluate how effectively agents make concessions.

    Maximum score: 15

    5 points - meaningful concessions
    5 points - gradual concessions
    5 points - avoids repeated offers
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

    # --------------------------------------------------------
    # COLLECT OFFERS BY AGENT
    # --------------------------------------------------------

    agent_offers = {}

    for config in configured_agents:

        role = get_config_value(
            config,
            "role",
            ""
        )

        agent_offers[role] = []

        for message in conversation:

            if message.get(
                "speaker"
            ) != role:
                continue

            values = extract_negotiation_values(
                message.get(
                    "message",
                    ""
                )
            )

            if values:
                # Use the final numerical value from each
                # message as the agent's current position.
                agent_offers[role].append(
                    values[-1]
                )

    # --------------------------------------------------------
    # NO NUMERICAL OFFERS
    # --------------------------------------------------------

    if not any(
        agent_offers.values()
    ):
        return 0

    meaningful_concessions = 0
    gradual_concessions = 0
    repeated_offers = 0

    # --------------------------------------------------------
    # ANALYZE EACH AGENT
    # --------------------------------------------------------

    for role, offers in agent_offers.items():

        if len(offers) < 2:
            continue

        previous_offer = None

        for offer in offers:

            if previous_offer is None:

                previous_offer = offer
                continue

            # Same offer repeated.
            if offer == previous_offer:

                repeated_offers += 1
                previous_offer = offer
                continue

            # Numerical movement occurred.
            meaningful_concessions += 1

            difference = abs(
                offer - previous_offer
            )

            percentage_change = (
                difference
                / abs(previous_offer)
                * 100
                if previous_offer != 0
                else 0
            )

            # Gradual movement:
            # more than 0% and up to 10%.
            if (
                0 < percentage_change <= 10
            ):
                gradual_concessions += 1

            previous_offer = offer

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    concession_score = 0

    if meaningful_concessions >= 1:
        concession_score += 5

    if gradual_concessions >= 1:
        concession_score += 5

    if repeated_offers == 0:
        concession_score += 5

    elif repeated_offers == 1:
        concession_score += 2

    return min(
        concession_score,
        15
    )


# ============================================================
# SCORE BREAKDOWN
# ============================================================

def calculate_score_breakdown(
    conversation,
    status,
    agent1_config=None,
    agent2_config=None
):
    # ========================================================
    # 1. OUTCOME — 30 POINTS
    # ========================================================

    if status == "agreement_reached":
        outcome_score = 30

    elif status == "deadlock":
        outcome_score = 15

    elif status == "max_rounds_reached":
        outcome_score = 10

    else:
        outcome_score = 0

    # ========================================================
    # 2. DEAL QUALITY — 25 POINTS
    # ========================================================

    if status == "agreement_reached":
        deal_quality_score = 25

    elif status == "deadlock":
        deal_quality_score = 10

    elif status == "max_rounds_reached":
        deal_quality_score = 5

    else:
        deal_quality_score = 0

    # ========================================================
    # 3. STRATEGY ADHERENCE — 20 POINTS
    # ========================================================

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

        # Keep the five strategies used by your UI.
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
            if get_config_value(
                config,
                "strategy",
                None
            ) in valid_strategies
        )

        if (
            valid_strategy_count
            == len(configured_agents)
        ):
            strategy_score = 20

        elif valid_strategy_count > 0:
            strategy_score = 10

        else:
            strategy_score = 0

    # ========================================================
    # 4. CONCESSION EFFICIENCY — 15 POINTS
    # ========================================================

    concession_score = (
        calculate_concession_score(
            conversation,
            agent1_config,
            agent2_config
        )
    )

    # ========================================================
    # 5. BOUNDARY MANAGEMENT — 10 POINTS
    # ========================================================

    boundary_score = (
        calculate_boundary_score(
            conversation,
            agent1_config,
            agent2_config
        )
    )

    # ========================================================
    # FINAL SCORE
    # ========================================================

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


# ============================================================
# TOTAL NEGOTIATION SCORE
# ============================================================

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


# ============================================================
# REPORT GENERATOR
# ============================================================

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

        # ====================================================
        # PARTICIPANTS
        # ====================================================

        participants = list({
            msg.get(
                "speaker",
                ""
            )
            for msg in conversation
            if msg.get(
                "speaker"
            )
        })

        # ====================================================
        # NEGOTIATION SPEAKERS
        # ====================================================

        negotiation_speakers = [
            "Buyer",
            "Supplier",
            "Candidate",
            "HR Manager",
            "Budget Requester",
            "Budget Allocator"
        ]

        # ====================================================
        # ROUND COUNT
        # ====================================================

        turn_count = sum(
            1
            for msg in conversation
            if msg.get(
                "speaker"
            ) in negotiation_speakers
        )

        total_rounds = (
            turn_count // 2
        )

        # ====================================================
        # AI SUMMARY
        # ====================================================

        try:

            summary = generate_summary(
                conversation,
                scenario,
                status
            )

        except Exception as e:

            print(
                "Summary Error:",
                e
            )

            summary = (
                "AI summary could not be generated."
            )

        # ====================================================
        # SCORE
        # ====================================================

        score_breakdown = (
            calculate_score_breakdown(
                conversation,
                status,
                agent1_config,
                agent2_config
            )
        )

        negotiation_score = (
            score_breakdown["total"]
        )

        # ====================================================
        # FINAL REPORT
        # ====================================================

        return {
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