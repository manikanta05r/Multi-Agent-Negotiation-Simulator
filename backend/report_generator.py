class ReportGenerator:

    def generate_report(self, session_id, conversation, status):

        participants = list(
            {
                msg["speaker"]
                for msg in conversation
            }
        )

        report = {
            "session_id": session_id,
            "status": status,
            "total_rounds": len(conversation),
            "participants": participants,
            "conversation": conversation
        }

        return report