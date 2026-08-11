import re

class AgreementDetector:

    def is_agreement(self, message: str) -> bool:

        message = message.lower()

        patterns = [

            # Explicit acceptance
            r"\bi accept\b",
            r"\bwe accept\b",

            r"\baccept this offer\b",
            r"\baccept the offer\b",
            r"\baccept your offer\b",

            r"\bam happy to accept\b",
            r"\bhappy to accept\b",

            r"\bam pleased to accept\b",
            r"\bpleased to accept\b",

            r"\bgladly accept\b",

            r"\boffer accepted\b",

            # Agreement
            r"\bagreement reached\b",
            r"\bagreement confirmed\b",
            r"\bwe have reached an agreement\b",

            # Project / Vendor
            r"\bwe accept this\b",

            # Job Offer
            r"\bwelcome to the team\b"
        ]

        return any(
            re.search(pattern, message)
            for pattern in patterns
        )