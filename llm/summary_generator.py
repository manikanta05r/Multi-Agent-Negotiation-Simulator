from llm.gemini_client import generate_response


def generate_summary(conversation, scenario, status):
    """
    Generate a summary of the completed negotiation using Gemini.
    """

    conversation_text = ""

    for message in conversation:
        conversation_text += (
            f"{message['speaker']}: {message['message']}\n"
        )

    prompt = f"""
You are an AI assistant.

Summarize the following completed negotiation.

Scenario:
{scenario}

Outcome:
{status}

Conversation:
{conversation_text}

Instructions:
1. Write a summary in 3-5 sentences.
2. Mention only facts present in the conversation.
3. Do not invent prices, products, warranties, delivery terms, or agreements.
4. If something was not discussed, do not mention it.
5. After the summary, list the important facts as bullet points.
"""

    return generate_response(prompt)