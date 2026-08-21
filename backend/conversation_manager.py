from database.operations import (
    save_negotiation_message,
    fetch_negotiation_messages,
)


class ConversationManager:

    def __init__(self):
        self.conversations = {}

    # ============================================================
    # CREATE CONVERSATION
    # ============================================================

    def create_conversation(
        self,
        session_id: str
    ):
        self.conversations[session_id] = []

    # ============================================================
    # ADD MESSAGE
    # ============================================================

    def add_message(
        self,
        session_id: str,
        speaker: str,
        message: str
    ):
        if session_id not in self.conversations:
            self.create_conversation(session_id)

        conversation_message = {
            "speaker": speaker,
            "message": message
        }

        # Keep the live conversation in memory.
        self.conversations[session_id].append(
            conversation_message
        )

        # Persist the message in Supabase.
        try:
            save_negotiation_message(
                session_id=session_id,
                speaker=speaker,
                message=message
            )

        except Exception as e:
            # Database failure should not break
            # the live negotiation.
            print(
                f"Warning: Failed to save message "
                f"to database: {e}"
            )

    # ============================================================
    # GET CONVERSATION
    # ============================================================

    def get_conversation(
        self,
        session_id: str
    ):
        # --------------------------------------------------------
        # 1. Return active in-memory conversation when available.
        # --------------------------------------------------------

        if session_id in self.conversations:

            return self.conversations[session_id]

        # --------------------------------------------------------
        # 2. Conversation is not in memory.
        #    Try loading it from Supabase.
        # --------------------------------------------------------

        try:

            persisted_messages = (
                fetch_negotiation_messages(
                    session_id
                )
            )

            if persisted_messages:

                conversation = []

                for message in persisted_messages:

                    conversation.append({
                        "speaker": message.get(
                            "speaker",
                            ""
                        ),
                        "message": message.get(
                            "message",
                            ""
                        )
                    })

                # Cache the recovered conversation
                # so subsequent calls do not hit the DB.
                self.conversations[session_id] = (
                    conversation
                )

                return conversation

        except Exception as e:

            print(
                f"Warning: Failed to load conversation "
                f"from database: {e}"
            )

        # --------------------------------------------------------
        # 3. No conversation found.
        # --------------------------------------------------------

        return []