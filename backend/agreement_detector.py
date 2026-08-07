import re

class AgreementDetector:

    def is_agreement(self, message: str) -> bool:

        message = message.lower()

        patterns = [
            r"\bi accept\b",
            r"\bi accept the offer\b",
            r"\bi accept your offer\b",
            r"\bi accept your final offer\b",
            r"\bi am pleased to accept\b",
            r"\bi am happy to accept\b",
            r"\bi'm happy to accept\b",

            r"\bwe accept\b",
            r"\bwe are delighted to accept\b",
            r"\baccept your decision\b",

            r"\boffer accepted\b",
            r"\bagreement reached\b",
            r"\bagreement confirmed\b",
            r"\bwelcome to the team\b"
        ]

        return any(re.search(pattern, message) for pattern in patterns)