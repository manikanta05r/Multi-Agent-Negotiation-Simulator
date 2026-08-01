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

    # Detect explicit acceptance
    if (
        "i accept" in text
        or "i agree" in text
        or "offer accepted" in text
        or "accepted your offer" in text
        or "we have a deal" in text
    ):
        result["agreement"] = True
        result["decision"] = "accept"

    elif "reject" in text or "cannot accept" in text:
        result["decision"] = "reject"

    else:
        result["decision"] = "counter_offer"

    return result