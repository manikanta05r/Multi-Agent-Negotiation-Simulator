class AgreementDetector:

    AGREEMENT_KEYWORDS = [
        "agree",
        "accepted",
        "accept",
        "deal",
        "final",
        "confirmed"
    ]

    def is_agreement(self, message: str) -> bool:
        message = message.lower()

        for keyword in self.AGREEMENT_KEYWORDS:
            if keyword in message:
                return True

        return False