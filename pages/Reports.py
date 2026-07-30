import streamlit as st
import pandas as pd

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

with col1:
    st.metric("Total Negotiations", "128", "+12")

with col2:
    st.metric("Successful Agreements", "102", "+8")

with col3:
    st.metric("Success Rate", "79.6%", "+2.1%")

with col4:
    st.metric("Average Rounds", "6.2", "-0.3")

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

history = pd.DataFrame({

    "Scenario":[
        "Buyer vs Supplier",
        "HR vs Candidate",
        "Budget Allocation",
        "Buyer vs Supplier",
        "Custom"
    ],

    "Rounds":[
        5,
        8,
        6,
        7,
        9
    ],

    "Result":[
        "Agreement",
        "Agreement",
        "Failed",
        "Agreement",
        "Agreement"
    ],

    "Final Offer":[
        "$20",
        "$65K",
        "$180K",
        "$18",
        "$250"
    ]

})

st.dataframe(
    history,
    use_container_width=True
)

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Report Summary")

st.success("""
### Key Insights

✅ High overall agreement rate

✅ Buyer vs Supplier is the most common scenario

✅ Average negotiation completes within 6 rounds

✅ AI agents consistently reach mutually beneficial agreements
""")

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