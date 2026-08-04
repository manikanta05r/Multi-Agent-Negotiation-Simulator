from llm.summary_generator import generate_summary


class ReportGenerator:

    def generate_report(
        self,
        session_id,
        conversation,
        status,
        scenario
    ):

        participants = list(
            {
                msg["speaker"]
                for msg in conversation
            }
        )

        total_rounds = sum(
            1
            for msg in conversation
            if msg["speaker"].lower() == "buyer"
        )

        try:
            summary = generate_summary(
                conversation,
                scenario,
                status
            )

        except Exception as e:
            print("Summary Error:", e)

            summary = "AI summary could not be generated."

        report = {
            "session_id": session_id,
            "scenario": scenario,
            "status": status,
            "total_rounds": total_rounds,
            "participants": participants,
            "summary": summary,
            "conversation": conversation
        }

        return report