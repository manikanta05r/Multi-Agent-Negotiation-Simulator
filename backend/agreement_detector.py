import re

class AgreementDetector:

    def is_agreement(self, message: str) -> bool:

        message = message.lower()

        patterns = [

            # Explicit acceptance
            r"\bi can accept\b",
            r"\bi accept\b",
            r"\bwe accept\b",
            r"\baccept this offer\b",
            r"\baccept the offer\b",
            r"\baccept your offer\b",
            r"\baccept your proposal\b",

            # Positive acceptance
            r"\bam happy to accept\b",
            r"\bhappy to accept\b",
            r"\bam pleased to accept\b",
            r"\bpleased to accept\b",
            r"\bgladly accept\b",

            # Finalization
            r"\bfinalize this agreement\b",
            r"\bfinalize the agreement\b",
            r"\bfinalize this order\b",
            r"\bpleased to finalize\b",
            r"\bdelighted to finalize\b",

            # Agreement confirmation
            r"\boffer accepted\b",
            r"\bagreement reached\b",
            r"\bagreement confirmed\b",
            r"\bwe have reached an agreement\b",
            r"\bconfirm our agreement\b",
            r"\bconfirming our agreement\b",
            r"\bagreement is successfully concluded\b",

            # Proceeding after agreement
            r"\bready to proceed\b",
            r"\bready to finalize\b",

            # Project / Vendor
            r"\bwe accept this\b",

            # Job Offer
            r"\bwelcome to the team\b"
        ]

        return any(
            re.search(pattern, message)
            for pattern in patterns
        )