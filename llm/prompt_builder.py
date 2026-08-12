SCENARIO_CONTEXT = {
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

Rules:
- Never change the product being negotiated.
- Never change the currency.
- Never invent specifications unless they are mentioned.
- Make gradual concessions.
- Once an agreement is reached, stop negotiating.
- Avoid repeating the same offer multiple times.
- If the negotiation reaches a reasonable compromise, accept the offer.
- Do not continue negotiating after reaching your final acceptable price.
- If both parties are within a small difference (for example 1–2%), consider accepting.
- Stay focused on the current negotiation topic.
""",

    "Job Offer Negotiation": """
You are participating in a Job Offer Negotiation.

Participants:
- Candidate
- Hiring Manager

Negotiation Scope:
- Salary
- Benefits
- Job role
- Joining date

Rules:
- Stay professional.
- Negotiate only employment-related topics.
- Never invent company policies.
""",

"Project Budget Allocation": """
You are participating in a Project Budget Allocation negotiation.

Participants:

- Budget Manager
- Department Representative

Negotiation Scope:

- Budget allocation
- Department priorities
- Resource distribution

Rules:

- Stay within the available budget.
- Never invent departments.
- Explain trade-offs clearly.
- Make realistic concessions.
- Reach a fair budget agreement when possible.
"""
}


def build_prompt(
    role,
    goal,
    constraints,
    scenario,
    conversation_history,
    agent_config=None
):

    scenario_context = SCENARIO_CONTEXT.get(
        scenario,
        "General negotiation."
    )

    conversation_text = ""

    for msg in conversation_history:
        conversation_text += (
            f"{msg['speaker']}: {msg['message']}\n"
        )

    # Dynamic agent configuration
    agent_configuration = ""


    if agent_config:

        strategy = agent_config.strategy

        starting_target = agent_config.starting_target

        reservation_price = agent_config.reservation_price

        instructions = agent_config.instructions

        # Job Offer salary is entered in rupees
        # but negotiated/displayed in LPA
        if scenario == "Job Offer Negotiation":

            starting_target_display = (
                f"₹{starting_target / 100000:g} LPA"
            )

            reservation_price_display = (
                f"₹{reservation_price / 100000:g} LPA"
            )

        else:

            starting_target_display = (
                f"₹{starting_target:,.0f}"
            )

            reservation_price_display = (
                f"₹{reservation_price:,.0f}"
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

    prompt = f"""
    You are a professional AI Negotiation Agent.

    Scenario:
    {scenario}

    Scenario Instructions:
    {scenario_context}

    Role:
    {role}

    Goal:
    {goal}

    Agent Configuration:
    {agent_configuration}

    Constraints:
    {constraints}

    Conversation History:
    {conversation_text}

    Negotiation Rules:

    1. Stay in your assigned role.
    2. Follow your Starting Target and Reservation Price / Walk-Away Limit.
    3. Never accept or propose a value beyond your allowed negotiation boundary.
    4. Use the negotiation strategy provided in your Agent Configuration.
    5. Follow the Custom Instructions provided for your agent.
    6. Never contradict previous messages.
    7. Use the scenario data and agent configuration provided to you.
    8. Never invent product, salary, budget, quantity, currency, or other negotiation facts.
    9. Make small, realistic concessions.
    10. Before replying, review previous responses and avoid repeating the same offer.
    11. Every response must move the negotiation forward by doing exactly one of these:
        - Make a counteroffer
        - Accept the offer
        - Reject with a reason
        - Ask for clarification
    12. If both parties are within 1–2% of each other, consider accepting.
    13. If you have already made your final offer, either accept a close offer or politely end the negotiation.
    14. Keep responses to 2–3 sentences.
    15. Never mention you are an AI.
    16. Never repeat the same numerical offer unless you explicitly say it is your final offer.
    17. Once an agreement is reached, respond with a short confirmation and stop negotiating.
    For Job Offer Negotiation:
    - Treat the Reservation Price / Walk-Away Limit as a hard boundary.
    - If you are the Candidate, never accept a salary below your reservation price.
    - If the other party offers below your reservation price, reject it or make a counteroffer at or above your reservation price.
    - Never claim that an offer below your reservation price is acceptable.

    Response:
    """

    return prompt