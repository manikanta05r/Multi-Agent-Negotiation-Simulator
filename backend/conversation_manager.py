class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def create_conversation(self, session_id: str):
        self.conversations[session_id] = []

    def add_message(self, session_id: str, speaker: str, message: str):
        if session_id not in self.conversations:
            self.create_conversation(session_id)

        self.conversations[session_id].append({
            "speaker": speaker,
            "message": message
        })

    def get_conversation(self, session_id: str):
        return self.conversations.get(session_id, [])