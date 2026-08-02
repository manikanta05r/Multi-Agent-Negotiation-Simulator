import streamlit as st
import pandas as pd
import requests

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
# Header
# ==========================================

session_id = st.session_state.get("session_id")

if not session_id:
    st.warning("No negotiation report available. Please complete a negotiation first.")
    st.stop()
try:
    response = requests.get(
        f"http://127.0.0.1:8000/report/{session_id}"
    )

    report = response.json()

    if "error" in report:
        st.error(report["error"])
        st.stop()

except Exception as e:
    st.error(f"Backend Error: {e}")
    st.stop()

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

col1, col2, col3, col4 = st.columns(4)

if report:

    with col1:
        st.metric("Scenario", report["scenario"])

    with col2:
        st.metric("Status", report["status"])

    with col3:
        st.metric("Rounds", report["total_rounds"])

    with col4:
        st.metric("Participants", len(report["participants"]))

else:

    with col1:
        st.metric("Scenario", "-")

    with col2:
        st.metric("Status", "-")

    with col3:
        st.metric("Rounds", "-")

    with col4:
        st.metric("Participants", "-")
st.divider()

# ==========================================
# Charts
# ==========================================

st.subheader("📉 Negotiation Analytics")

left, right = st.columns(2)

with left:

    st.markdown("### Success Trend")

    trend = pd.DataFrame({
        "Negotiations":[1,2,3,4,5,6,7],
        "Success":[65,70,75,80,78,82,85]
    })

    st.line_chart(
        trend.set_index("Negotiations")
    )

with right:

    st.markdown("### Scenario Distribution")

    scenario = pd.DataFrame({
        "Scenario":[
            "Buyer-Supplier",
            "HR-Candidate",
            "Budget",
            "Custom"
        ],
        "Count":[40,30,25,33]
    })

    st.bar_chart(
        scenario.set_index("Scenario")
    )

st.divider()

# ==========================================
# Negotiation History
# ==========================================

st.subheader("📋 Negotiation History")

if report:

    history = pd.DataFrame([
        {
            "Scenario": report["scenario"],
            "Rounds": report["total_rounds"],
            "Status": report["status"],
            "Participants": ", ".join(report["participants"])
        }
    ])

else:

    history = pd.DataFrame()

st.dataframe(
    history,
    use_container_width=True
)

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Report Summary")

if report:

    st.success(report["summary"])

else:

    st.warning("No report available.")

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

    st.button(
        "📄 Generate PDF Report",
        use_container_width=True
    )

st.divider()

if st.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("pages/Home.py")