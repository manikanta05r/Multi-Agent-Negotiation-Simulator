class DeadlockDetector:

    def is_deadlock(self, conversation):

        if len(conversation) < 6:
            return False

        last_messages = conversation[-6:]

        buyer_messages = [
            msg["message"]
            for msg in last_messages
            if msg["speaker"] == "Buyer"
        ]

        if len(set(buyer_messages)) == 1:
            return True

        return False