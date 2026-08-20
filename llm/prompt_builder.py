# ============================================================
# SCENARIO CONTEXT
# ============================================================

SCENARIO_CONTEXT = {

    # ========================================================
    # VENDOR PRICING NEGOTIATION
    # ========================================================

    "Vendor Pricing Negotiation": """
You are participating in a Vendor Pricing Negotiation.

Participants:
- Buyer
- Supplier

Negotiation Scope:
- Product price
- Quantity
- Delivery terms
- Payment terms

NEGOTIATION POSITIONS:

Buyer:
- Starting Target = opening price.
- Reservation Price = maximum acceptable price.
- Normally starts low and gradually moves upward.

Supplier:
- Starting Target = opening price.
- Reservation Price = minimum acceptable price.
- Normally starts high and gradually moves downward.

The Starting Target is the normal opening position.

The Reservation Price is the final negotiation boundary.

Use gradual concessions rather than large sudden changes.

COMMUNICATION STYLE:

- Be professional and cooperative.
- Acknowledge the other party's reasoning.
- Explain why the current offer is acceptable or insufficient.
- Make realistic counteroffers.
- Ask constructive questions when useful.
- Avoid sounding robotic.
- Avoid repeating exactly the same sentence.
- Keep the negotiation moving.

IMPORTANT:

A proposal is NOT an agreement.

Phrases such as:
- "Could we agree on..."
- "Would you consider..."
- "We propose..."
- "Perhaps we can..."
- "Can we meet at..."

are proposals, not acceptance.

Only clearly accepting the other party's latest offer should indicate agreement.

Once both parties explicitly agree, stop negotiating.
""",

    # ========================================================
    # JOB OFFER NEGOTIATION
    # ========================================================

    "Job Offer Negotiation": """
You are participating in a Job Offer Negotiation.

Participants:
- Candidate
- HR Manager

Negotiation Scope:
- Salary
- Benefits
- Job role
- Joining date

SALARY POSITIONS:

Candidate:
- Starting Target = initial salary request.
- Reservation Price = minimum acceptable salary.
- Normally starts high and gradually moves downward.

HR Manager:
- Starting Target = initial salary offer.
- Reservation Price = maximum salary HR can approve.
- Normally starts low and gradually moves upward.

The Starting Target is the opening negotiation position.

The Reservation Price is the final boundary.

NEGOTIATION STYLE:

- Be professional and realistic.
- Acknowledge the other party's position.
- Explain the reasoning behind salary changes.
- Make gradual concessions.
- Discuss benefits or joining date when useful.
- Keep the conversation natural.

IMPORTANT:

A suggestion is not an agreement.

Statements such as:
- "Could we agree on..."
- "Would you consider..."
- "We could potentially..."
- "Perhaps we can meet at..."
- "I would propose..."

are still negotiation.

Only explicit acceptance should conclude the negotiation.

Once both parties agree, stop negotiating.
""",

    # ========================================================
    # PROJECT BUDGET ALLOCATION
    # ========================================================

    "Project Budget Allocation": """
You are participating in a Project Budget Allocation negotiation.

Participants:
- Budget Requester
- Budget Allocator

Negotiation Scope:
- Project budget
- Department/project priorities
- Resource distribution

BUDGET POSITIONS:

Budget Requester:
- Starting Target = initial requested amount.
- Walk-Away Budget = minimum amount the requester can reasonably accept.
- Normally starts high and gradually moves downward.

Budget Allocator:
- Starting Target = initial offered amount.
- Walk-Away Budget = maximum amount the allocator can reasonably approve.
- Normally starts low and gradually moves upward.

IMPORTANT:

The Total Project Budget represents the overall financial pool.

It is NOT automatically:
- the allocator's opening offer
- the allocator's walk-away amount
- a counteroffer
- a compromise amount

Each agent should use its own configured Starting Target when making its opening numerical position.

NEGOTIATION BEHAVIOR:

Budget Requester should generally move like:

Starting Target
→ lower request
→ lower request
→ lower request
→ Walk-Away Budget

Budget Allocator should generally move like:

Starting Target
→ higher offer
→ higher offer
→ higher offer
→ Walk-Away Budget

Concessions should feel gradual and realistic.

Do not jump immediately to the final boundary unless the negotiation naturally requires it.

COMMUNICATION STYLE:

The conversation should feel like two professional people solving a problem.

For example:

Requester:
"I understand the current funding pressure. However, ₹2,400,000 would leave several critical deliverables underfunded. We could reduce our request to ₹2,650,000 if the allocator can move closer to that level."

Allocator:
"I appreciate the reduction. ₹2,650,000 is still above our current capacity, but we can increase our offer to ₹2,450,000 to keep the discussion moving."

This is negotiation.

Do not immediately declare deadlock.

IMPORTANT AGREEMENT RULE:

A proposal is NOT an agreement.

These are proposals:

- "Could we agree on ₹2,550,000?"
- "Can we meet at ₹2,550,000?"
- "Would you consider ₹2,550,000?"
- "Perhaps we can compromise at ₹2,550,000."
- "I propose ₹2,550,000."

These statements mean the negotiation is still active.

Only statements such as:

- "We accept your offer."
- "We agree to ₹2,550,000."
- "We confirm the agreement at ₹2,550,000."
- "That works for us. We accept."

should communicate acceptance.

Do not claim that an agreement has been reached merely because a compromise was proposed.

If the two positions are still different, continue negotiating.

If your boundary has been reached, explain that it is your maximum/minimum and invite the other party to respond.

Do not repeatedly say "the negotiation is over" unless the system has actually ended the negotiation.

Do not mention that you are an AI.

Keep each response to approximately 2–4 sentences.
"""
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _extract_numeric_offers(
    conversation_history,
    role
):
    """
    Extract numerical values from the conversation.

    This is intentionally lightweight. It does not attempt to
    understand every sentence. It identifies likely monetary
    values associated with each speaker.
    """

    import re

    offers = []

    if not conversation_history:
        return offers

    for msg in conversation_history:

        if msg.get("speaker") != role:
            continue

        text = msg.get("message", "")

        if not text:
            continue

        # Supports:
        # ₹2,500,000
        # ₹25,00,000
        # ₹2500000
        # 2500000
        # ₹25 LPA
        # ₹25 lakh
        # ₹25 lakhs
        patterns = [
            r"₹\s*([\d,]+(?:\.\d+)?)",
            r"\b([\d,]+(?:\.\d+)?)\s*(?:lpa|lakh|lakhs)\b",
            r"\b([\d,]+(?:\.\d+)?)\b"
        ]

        found_values = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for value in matches:

                try:
                    numeric = float(
                        value.replace(",", "")
                    )
                except (TypeError, ValueError):
                    continue

                # Ignore obviously irrelevant small numbers.
                if numeric >= 10000:
                    found_values.append(
                        numeric
                    )

        if found_values:

            # Use the last meaningful number in the message.
            offers.append(
                found_values[-1]
            )

    return offers


def _get_latest_offer(
    conversation_history,
    role
):
    """
    Return the latest numerical position made by a speaker.
    """

    offers = _extract_numeric_offers(
        conversation_history,
        role
    )

    if not offers:
        return None

    return offers[-1]


def _format_money(
    value,
    scenario
):
    """
    Format negotiation values for the prompt.
    """

    if value is None:
        return "Not available"

    if scenario == "Job Offer Negotiation":

        return (
            f"₹{value / 100000:g} LPA"
        )

    return (
        f"₹{value:,.0f}"
    )


def _clamp(
    value,
    minimum,
    maximum
):
    """
    Keep a value inside a valid negotiation boundary.
    """

    return max(
        minimum,
        min(value, maximum)
    )


def _calculate_suggested_position(
    scenario,
    role,
    starting_target,
    reservation_price,
    own_previous_offer,
    opponent_latest_offer
):
    """
    Calculate a conservative next numerical position.

    IMPORTANT:
    Python determines the suggested numerical position.

    Gemini's job is to communicate that position naturally.
    """

    if (
        starting_target is None
        or reservation_price is None
    ):
        return None

    # --------------------------------------------------------
    # No previous offer
    # --------------------------------------------------------

    if own_previous_offer is None:

        return starting_target

    # --------------------------------------------------------
    # No opponent offer yet
    # --------------------------------------------------------

    if opponent_latest_offer is None:

        return own_previous_offer

    # --------------------------------------------------------
    # Determine movement direction
    # --------------------------------------------------------

    moves_upward = (
        reservation_price > starting_target
    )

    moves_downward = (
        reservation_price < starting_target
    )

    # --------------------------------------------------------
    # Gradual concession
    #
    # Move approximately 25% of the distance between our
    # previous position and the opponent's latest position.
    # --------------------------------------------------------

    distance = (
        opponent_latest_offer
        - own_previous_offer
    )

    concession = (
        distance * 0.25
    )

    suggested = (
        own_previous_offer
        + concession
    )

    # --------------------------------------------------------
    # Respect direction
    # --------------------------------------------------------

    if moves_upward:

        # We should normally move upward.
        suggested = max(
            suggested,
            own_previous_offer
        )

        suggested = _clamp(
            suggested,
            starting_target,
            reservation_price
        )

    elif moves_downward:

        # We should normally move downward.
        suggested = min(
            suggested,
            own_previous_offer
        )

        suggested = _clamp(
            suggested,
            reservation_price,
            starting_target
        )

    else:

        suggested = own_previous_offer

    # --------------------------------------------------------
    # Round monetary values sensibly.
    # --------------------------------------------------------

    if scenario == "Job Offer Negotiation":

        # Round salary to ₹5,000 increments.
        suggested = (
            round(suggested / 5000)
            * 5000
        )

    else:

        # Round other financial negotiations to ₹1,000.
        suggested = (
            round(suggested / 1000)
            * 1000
        )

    return _clamp(
        suggested,
        min(
            starting_target,
            reservation_price
        ),
        max(
            starting_target,
            reservation_price
        )
    )


# ============================================================
# NEGOTIATION STATE
# ============================================================

def _build_negotiation_state(
    role,
    scenario,
    conversation_history,
    agent_config
):
    """
    Build a deterministic negotiation state for the LLM.

    The important principle is:

        Python calculates the position.
        Gemini communicates the position.
    """

    if not agent_config:

        return {
            "own_previous_offer": None,
            "opponent_latest_offer": None,
            "suggested_position": None,
            "state_text": (
                "No numerical agent configuration is available. "
                "Do not invent financial boundaries."
            )
        }

    starting_target = getattr(
        agent_config,
        "starting_target",
        None
    )

    reservation_price = getattr(
        agent_config,
        "reservation_price",
        None
    )

    # --------------------------------------------------------
    # Determine opponent role.
    # --------------------------------------------------------

    opponent_role = None

    if scenario == "Vendor Pricing Negotiation":

        if role == "Buyer":
            opponent_role = "Supplier"
        else:
            opponent_role = "Buyer"

    elif scenario == "Job Offer Negotiation":

        if role == "Candidate":
            opponent_role = "HR Manager"
        else:
            opponent_role = "Candidate"

    elif scenario == "Project Budget Allocation":

        if role == "Budget Requester":
            opponent_role = "Budget Allocator"
        else:
            opponent_role = "Budget Requester"

    # --------------------------------------------------------
    # Find latest positions.
    # --------------------------------------------------------

    own_previous_offer = _get_latest_offer(
        conversation_history,
        role
    )

    opponent_latest_offer = _get_latest_offer(
        conversation_history,
        opponent_role
    )

    # --------------------------------------------------------
    # Calculate suggested next position.
    # --------------------------------------------------------

    suggested_position = _calculate_suggested_position(
        scenario=scenario,
        role=role,
        starting_target=starting_target,
        reservation_price=reservation_price,
        own_previous_offer=own_previous_offer,
        opponent_latest_offer=opponent_latest_offer
    )

    # --------------------------------------------------------
    # Determine movement.
    # --------------------------------------------------------

    if (
        own_previous_offer is None
        and starting_target is not None
    ):

        movement_instruction = (
            "This is your opening numerical position. "
            "Use your Starting Target."
        )

    elif suggested_position is None:

        movement_instruction = (
            "No deterministic numerical position could be "
            "calculated. Do not invent a financial boundary."
        )

    elif own_previous_offer is None:

        movement_instruction = (
            "Use the configured Starting Target as your "
            "opening position."
        )

    elif suggested_position > own_previous_offer:

        movement_instruction = (
            "Your next position should move upward gradually."
        )

    elif suggested_position < own_previous_offer:

        movement_instruction = (
            "Your next position should move downward gradually."
        )

    else:

        movement_instruction = (
            "Hold your current position unless the negotiation "
            "requires a justified change."
        )

    # --------------------------------------------------------
    # Build state text.
    # --------------------------------------------------------

    state_text = f"""
CURRENT NEGOTIATION STATE

Your role:
{role}

Your Starting Target:
{_format_money(starting_target, scenario)}

Your Reservation Price / Walk-Away Limit:
{_format_money(reservation_price, scenario)}

Your previous numerical offer:
{_format_money(own_previous_offer, scenario)}

Opponent's latest numerical offer:
{_format_money(opponent_latest_offer, scenario)}

Python-calculated suggested next position:
{_format_money(suggested_position, scenario)}

Movement guidance:
{movement_instruction}

IMPORTANT NUMERICAL RULE:

Python has calculated the suggested next numerical position.

If you make a numerical counteroffer, use the Python-calculated
suggested next position rather than inventing a substantially
different number.

Your task is to explain and communicate that position naturally.

Do not jump directly to your reservation boundary unless the
negotiation genuinely requires it.

Do not move outside your configured reservation boundary.

Do not treat the opponent's proposal as an agreement.
"""

    return {
        "own_previous_offer": own_previous_offer,
        "opponent_latest_offer": opponent_latest_offer,
        "suggested_position": suggested_position,
        "state_text": state_text
    }


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(
    role,
    goal,
    constraints,
    scenario,
    conversation_history,
    agent_config=None
):

    # --------------------------------------------------------
    # SCENARIO CONTEXT
    # --------------------------------------------------------

    scenario_context = SCENARIO_CONTEXT.get(
        scenario,
        "General negotiation."
    )

    # --------------------------------------------------------
    # CONVERSATION HISTORY
    # --------------------------------------------------------

    conversation_text = ""

    for msg in conversation_history:

        conversation_text += (
            f"{msg['speaker']}: {msg['message']}\n"
        )

    # --------------------------------------------------------
    # AGENT CONFIGURATION
    # --------------------------------------------------------

    agent_configuration = ""

    starting_target_display = "Not configured"
    reservation_price_display = "Not configured"

    if agent_config:

        strategy = getattr(
            agent_config,
            "strategy",
            ""
        )

        starting_target = getattr(
            agent_config,
            "starting_target",
            None
        )

        reservation_price = getattr(
            agent_config,
            "reservation_price",
            None
        )

        instructions = getattr(
            agent_config,
            "instructions",
            ""
        )

        # ----------------------------------------------------
        # DISPLAY VALUES
        # ----------------------------------------------------

        starting_target_display = _format_money(
            starting_target,
            scenario
        )

        reservation_price_display = _format_money(
            reservation_price,
            scenario
        )

        agent_configuration = f"""
Negotiation Strategy:
{strategy}

Starting Target:
{starting_target_display}

Reservation Price / Walk-Away Limit:
{reservation_price_display}

Custom Instructions:
{instructions}
"""

    # ========================================================
    # PYTHON NEGOTIATION STATE
    # ========================================================

    negotiation_state = _build_negotiation_state(
        role=role,
        scenario=scenario,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # ========================================================
    # MAIN PROMPT
    # ========================================================

    prompt = f"""
You are a professional negotiation agent participating in
a live multi-agent negotiation.

============================================================
SCENARIO
============================================================

{scenario}

============================================================
SCENARIO-SPECIFIC GUIDANCE
============================================================

{scenario_context}

============================================================
YOUR ROLE
============================================================

Role:
{role}

Goal:
{goal}

Constraints:
{constraints}

============================================================
YOUR NEGOTIATION CONFIGURATION
============================================================

{agent_configuration}

============================================================
AUTHORITATIVE VALUES
============================================================

Starting Target:
{starting_target_display}

Reservation Price / Walk-Away Limit:
{reservation_price_display}

These values describe your negotiation position.

The Starting Target is your opening position.

The Reservation Price / Walk-Away Limit is your final boundary.

Do not confuse the two.

============================================================
PYTHON-CALCULATED NEGOTIATION STATE
============================================================

{negotiation_state["state_text"]}

============================================================
OPENING POSITION
============================================================

If you are making the first numerical offer for your side,
use your configured Starting Target.

Do not invent a completely unrelated opening value.

After the opening position, use the Python-calculated
negotiation state to guide your next numerical position.

============================================================
CONVERSATION HISTORY
============================================================

{conversation_text}

============================================================
HOW TO NEGOTIATE
============================================================

1. Read the entire conversation before responding.

2. Respond as the assigned role.

3. Directly address the other agent's latest message.

4. Acknowledge useful concessions made by the other party.

5. Explain your position briefly.

6. Make a reasonable counteroffer when appropriate.

7. Use the Python-calculated suggested position when
   making a numerical counteroffer.

8. Make gradual concessions.

9. Avoid repeating the exact same numerical offer unless
   there is a strategic reason to hold your position.

10. Keep the conversation moving.

11. Do not immediately declare deadlock.

12. If the other party refuses your offer, try another
    reasonable response before declaring that no agreement
    is possible.

13. If your boundary has been reached, clearly explain that
    you cannot move further and invite the other party to
    consider your position.

14. Never knowingly make an offer outside your configured
    Reservation Price / Walk-Away Limit.

15. Do not use the Total Project Budget as your opening offer
    unless it is explicitly configured as your Starting Target.

16. Do not invent financial limits.

17. Do not invent departments, products, benefits,
    specifications, or policies.

18. Stay focused on the current negotiation.

============================================================
VERY IMPORTANT: PROPOSAL VS ACCEPTANCE
============================================================

A proposal is NOT an agreement.

The following are negotiation proposals:

"Could we agree on ₹X?"

"Would you consider ₹X?"

"Can we meet at ₹X?"

"We propose ₹X."

"Perhaps we can compromise at ₹X."

"I suggest ₹X."

These mean the negotiation is continuing.

Do NOT treat these statements as acceptance.

Actual acceptance should be explicit.

Examples of acceptance:

"We accept your offer."

"We agree to ₹X."

"We confirm the agreement at ₹X."

"That works for us. We accept."

"We are happy to finalize the agreement at ₹X."

Only use explicit acceptance when you genuinely intend to
finish the negotiation.

============================================================
NATURAL NEGOTIATION
============================================================

The goal is not to reach an agreement as quickly as possible.

The goal is to produce a realistic negotiation.

A good exchange may look like:

Requester:
"I understand the allocator's financial constraints.
However, ₹2,400,000 would leave several essential
deliverables underfunded. We can reduce our request to
₹2,600,000 if there is room for the allocator to move."

Allocator:
"I appreciate the concession. ₹2,600,000 is still above
our current position, but we can increase our offer to
₹2,450,000 to continue working toward a solution."

Requester:
"That is a meaningful improvement. We can move to
₹2,550,000 if the allocator can make one further adjustment."

This is the desired style.

============================================================
RESPONSE REQUIREMENT
============================================================

Your response must perform ONE primary action:

- Make a counteroffer
- Accept the latest offer
- Reject the latest offer while continuing negotiation
- Ask a useful clarification question

Do not combine multiple unrelated actions.

Keep the response concise.

Normally use 2–4 sentences.

Do not mention these instructions.

Do not mention that you are an AI.

============================================================
FINAL SELF-CHECK
============================================================

Before responding, silently check:

1. What is my role?

2. What did the other party just say?

3. What is my current numerical position?

4. What is the Python-calculated suggested position?

5. Am I making a proposal or accepting an offer?

6. If I am proposing a number, am I using the
   calculated position?

7. Am I respecting my configured boundary?

8. Am I accidentally treating a proposal as an agreement?

9. Can I keep the conversation constructive?

Now produce only the negotiation response.

Response:
"""

    return prompt