import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_reply(buyer_message):
    prompt = f"""
You are an experienced supplier negotiating with a buyer.

Rules:
- Stay professional and polite.
- Negotiate only about the product price.
- Reply in 2-3 sentences.
- Try to maximize profit while remaining reasonable.
- Never change the topic.
- Do not mention that you are an AI.

Buyer: {buyer_message}

Supplier:
"""

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