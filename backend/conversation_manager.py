from database.operations import save_negotiation_message


class ConversationManager:

    def __init__(self):
        self.conversations = {}

    def create_conversation(self, session_id: str):
        self.conversations[session_id] = []

    def add_message(
        self,
        session_id: str,
        speaker: str,
        message: str
    ):
        if session_id not in self.conversations:
            self.create_conversation(session_id)

        # Keep the existing in-memory conversation.
        self.conversations[session_id].append({
            "speaker": speaker,
            "message": message
        })

        # Persist the message in Supabase.
        try:
            save_negotiation_message(
                session_id=session_id,
                speaker=speaker,
                message=message
            )
        except Exception as e:
            # Do not break the live negotiation
            # if database persistence fails.
            print(
                f"Warning: Failed to save message "
                f"to database: {e}"
            )

    def get_conversation(self, session_id: str):
        return self.conversations.get(
            session_id,
            []
        )