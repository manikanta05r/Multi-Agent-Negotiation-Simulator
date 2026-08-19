import streamlit as st
import pandas as pd
import requests

from utils.pdf_generator import generate_pdf_report

from components.styles import load_css
from components.navbar import show_navbar

st.set_page_config(
    page_title="Reports",
    page_icon="📊",
    layout="wide"
)

load_css()
show_navbar()

# ==========================================
# Get Negotiation History
# ==========================================

try:

    response = requests.get(
        "http://127.0.0.1:8000/reports/history",
        timeout=10
    )

    if response.status_code == 200:
        history_data = response.json()
    else:
        history_data = []
        st.error("Unable to fetch negotiation history.")

except Exception as e:

    history_data = []
    st.error(f"Backend connection failed.\n\n{e}")




st.title("📊 Negotiation Reports & Analytics")

st.markdown("""
Analyze completed negotiations, monitor performance metrics,
and export negotiation reports.
""")

st.divider()


# ==========================================
# KPI Metrics
# ==========================================

st.subheader("📈 Overall Performance")

total_negotiations = len(history_data)

agreements = sum(
    1
    for item in history_data
    if item.get("status") == "agreement_reached"
)

deadlocks = sum(
    1
    for item in history_data
    if item.get("status") == "deadlock"
)

max_rounds = sum(
    1
    for item in history_data
    if item.get("status") == "max_rounds_reached"
)

success_rate = (
    (agreements / total_negotiations) * 100
    if total_negotiations > 0
    else 0
)

average_score = (
    sum(
        item.get("negotiation_score", 0)
        for item in history_data
    ) / total_negotiations
    if total_negotiations > 0
    else 0
)

col1, col2, col3, col4, col5, col6 = st.columns(6)  

with col1:
    st.metric(
        "Total Negotiations",
        total_negotiations
    )

with col2:
    st.metric(
        "Agreements",
        agreements
    )

with col3:
    st.metric(
        "Deadlocks",
        deadlocks
    )

with col4:
    st.metric(
        "Max Rounds",
        max_rounds
    )

with col5:
    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%"
    )

with col6:
    st.metric(
        "Average Score",
        f"{average_score:.1f}/100"
    )

st.divider()

# ==========================================
# Charts
# ==========================================

st.subheader("📉 Negotiation Analytics")

left, right = st.columns(2)

with left:

    st.markdown("### Success Trend")

    completed = 0
    successful = 0

    trend_data = []

    for item in history_data:

        completed += 1

        if item.get("status") == "agreement_reached":
            successful += 1

        success_rate = (
            (successful / completed) * 100
            if completed > 0
            else 0
        )

        trend_data.append({
            "Negotiations": completed,
            "Success Rate": success_rate
        })

    trend = pd.DataFrame(trend_data)

    if not trend.empty:

        st.line_chart(
            trend.set_index("Negotiations")
        )

    else:

        st.info(
            "Complete negotiations to view the success trend."
        )

with right:

    st.markdown("### Scenario Distribution")

    scenario_counts = {}

    for item in history_data:

        scenario_name = item.get(
            "scenario",
            "Unknown"
        )

        scenario_counts[scenario_name] = (
            scenario_counts.get(scenario_name, 0) + 1
        )

    scenario = pd.DataFrame({
        "Scenario": list(scenario_counts.keys()),
        "Count": list(scenario_counts.values())
    })

    st.bar_chart(
        scenario.set_index("Scenario")
    )

st.divider()

# ==========================================
# Negotiation History
# ==========================================

st.subheader("📋 Negotiation History")

if history_data:

        history = pd.DataFrame([
        {
            "Session ID": item.get(
                "session_id",
                "-"
            ),
            "Scenario": item.get(
                "scenario",
                "-"
            ),
            "Mode": item.get(
                "mode",
                "-"
            ),
            "Rounds": item.get(
                "rounds",
                "-"
            ),
            "Score": item.get(
                "negotiation_score",
                "-"
            ),
            "Status": item.get(
                "status",
                "-"
            )
        }
        for item in history_data
    ])

else:

    history = pd.DataFrame(
        columns=[
            "Session ID",
            "Scenario",
            "Mode",
            "Rounds",
            "Score",
            "Status"
        ]
    )

st.dataframe(
    history,
    use_container_width=True
)

st.divider()

# ==========================================
# Score Breakdown
# ==========================================

st.subheader("📊 Negotiation Score Breakdown")

if history_data:

    selected_session = st.selectbox(
        "Select a negotiation to view its score breakdown",
        history_data,
        format_func=lambda item: (
            f"{item.get('session_id', '-')[:8]} — "
            f"{item.get('scenario', '-')} — "
            f"{item.get('negotiation_score', '-')}/100"
        )
    )

    score_breakdown = selected_session.get(
        "score_breakdown",
        {}
    )

    if score_breakdown:

        breakdown_data = {
            "Outcome": (
                score_breakdown.get("outcome", 0),
                30
            ),
            "Deal Quality": (
                score_breakdown.get("deal_quality", 0),
                25
            ),
            "Strategy Adherence": (
                score_breakdown.get(
                    "strategy_adherence",
                    0
                ),
                20
            ),
            "Concession Efficiency": (
                score_breakdown.get(
                    "concession_efficiency",
                    0
                ),
                15
            ),
            "Boundary Management": (
                score_breakdown.get(
                    "boundary_management",
                    0
                ),
                10
            )
        }

        for category, values in breakdown_data.items():

            score, maximum = values

            col1, col2, col3 = st.columns(
                [3, 1, 1]
            )

            with col1:
                st.write(
                    f"**{category}**"
                )

            with col2:
                st.write(
                    f"{score}/{maximum}"
                )

            with col3:
                st.progress(
                    score / maximum
                    if maximum > 0
                    else 0
                )

        st.divider()

        total_score = score_breakdown.get(
            "total",
            selected_session.get(
                "negotiation_score",
                0
            )
        )

        st.metric(
            "🏆 Total Negotiation Score",
            f"{total_score}/100"
        )

    else:

        st.info(
            "Score breakdown is not available for "
            "this negotiation."
        )

else:

    st.info(
        "Complete a negotiation to view the score breakdown."
    )

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Report Summary")

if history_data:

    st.success(
        f"{total_negotiations} completed negotiations found."
    )

else:

    st.warning(
        "No completed negotiations available."
    )

st.divider()

# ==========================================
# Export
# ==========================================

st.subheader("📥 Export Reports")

csv = history.to_csv(index=False)

col1, col2 = st.columns(2)

with col1:

    st.download_button(
        "⬇️ Download CSV Report",
        csv,
        file_name="negotiation_report.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:

    if st.button(
        "📄 Generate PDF Report",
        use_container_width=True
    ):

        pdf_path = "negotiation_report.pdf"

        generate_pdf_report(
            pdf_path,
            history_data
        )

        with open(

            pdf_path,
            "rb"
        ) as pdf_file:

            st.download_button(
                "⬇️ Download PDF Report",
                pdf_file,
                file_name="negotiation_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

st.divider()

if st.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("pages/Home.py")