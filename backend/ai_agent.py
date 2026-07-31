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

    # Build prompt
    prompt = f"""
You are an experienced supplier participating in a negotiation.

Scenario:
{scenario}

Negotiation Mode:
{mode}

Rules:
- Stay professional and polite.
- Respond according to the given scenario.
- Negotiate only about the product or service in the scenario.
- Reply in 2-3 sentences.
- Try to maximize profit while remaining reasonable.
- Remember previous negotiation rounds.
- Never contradict your earlier responses.
- Never change the topic.
- Do not mention that you are an AI.

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

    1. A 3-5 sentence summary.
    2. Mention only facts present in the conversation.
    3. Do not invent offers, prices, products, or conditions.
    4. If something was not discussed, do not mention it.
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