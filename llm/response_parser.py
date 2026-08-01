import re


def parse_response(response):
    """
    Parse Gemini's response into structured data.
    """

    result = {
        "message": response.strip(),
        "offer": None,
        "decision": "counter_offer",
        "agreement": False
    }

    # Find all numbers, including numbers with commas
    matches = re.findall(r"\b\d[\d,]*\b", response)

    if matches:
        numbers = [int(number.replace(",", "")) for number in matches]

        # Use the last number as the proposed offer
        result["offer"] = numbers[-1]

    text = response.lower()

    # Explicit acceptance phrases only
    acceptance_phrases = [
        "i accept",
        "i agree",
        "offer accepted",
        "accepted your offer",
        "we have a deal",
        "deal is confirmed",
        "deal confirmed"
    ]

    # Explicit rejection phrases
    rejection_phrases = [
        "i reject",
        "offer rejected",
        "cannot accept",
        "can't accept",
        "do not accept",
        "not acceptable",
        "cannot approve",
        "can't approve",
        "not approved"
        "i decline",
        "decline the",
        "declined",
        "cannot approve"
    ]

    if any(phrase in text for phrase in acceptance_phrases):
        result["agreement"] = True
        result["decision"] = "accept"

    elif any(phrase in text for phrase in rejection_phrases):
        result["agreement"] = False
        result["decision"] = "reject"

    else:
        result["decision"] = "counter_offer"

    return result