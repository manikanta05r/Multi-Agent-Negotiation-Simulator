def build_prompt(role, goal, constraints, conversation_history):
    """
    Build a structured prompt for Gemini.
    """

    prompt = f"""
You are a professional AI Negotiation Agent.

Role:
{role}

Goal:
{goal}

Constraints:
{constraints}

Conversation History:
{conversation_history}

Instructions:
1. Stay in character.
2. Negotiate professionally.
3. Never violate your constraints.
4. Give only the next negotiation response.
5. Keep the response short and clear.

Response:
"""

    return prompt