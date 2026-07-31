class AgreementDetector:

    AGREEMENT_PHRASES = [
        "i accept",
        "i accept your offer",
        "i accept the offer",
        "i accept your final offer",
        "we have an agreement",
        "i agree",
        "agreement confirmed",
        "offer accepted"
    ]

    def is_agreement(self, message: str) -> bool:

        message = message.lower().strip()

        for phrase in self.AGREEMENT_PHRASES:
            if phrase in message:
                return True

        return False