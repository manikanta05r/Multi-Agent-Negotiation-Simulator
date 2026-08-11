import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_reply(conversation, scenario, mode):

    # Convert conversation list to text
    conversation_text = ""

    for message in conversation:
        conversation_text += (
            f"{message['speaker']}: {message['message']}\n"
        )

    prompt = f"""
    You are a professional supplier negotiating with a buyer.

    Scenario:
    {scenario}

    Negotiation Mode:
    {mode}

    Strict Rules:

    1. Stay professional and polite.
    2. Negotiate ONLY about the current scenario.
    3. Never invent product specifications, warranty, delivery terms, discounts, taxes, or conditions unless they already appear in the conversation.
    4. Use ONLY information from the conversation history.
    5. Never contradict your previous replies.
    6. If you reduce the price once, never increase it again.
    7. Make only small and reasonable concessions in each round.
    8. Never restart the negotiation.
    9. Reply in a maximum of 2-3 sentences.
    10. If the buyer accepts the offer, respond only with a short confirmation message and end the negotiation.
    11. Do not create new facts.
    12. Do not change the product being negotiated.
    13. If the buyer asks for information that is not available in the conversation, politely say that it is not available instead of inventing an answer.

    Conversation History:

    {conversation_text}

    Supplier:
    """

    print(prompt)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.choices[0].message.content

def generate_summary(conversation, scenario, status):

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

Provide:

        1. A summary in 3-5 sentences.
        2. Mention ONLY facts explicitly present in the conversation.
        3. Do NOT invent prices, specifications, discounts, warranties, products, delivery terms, or conditions.
        4. Do NOT infer missing information.
        5. If a detail was not discussed, omit it completely.
        6. End with the final negotiation outcome
    """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=200
        )

        return response.choices[0].message.content