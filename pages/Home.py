import streamlit as st

from components.styles import load_css
from components.navbar import show_navbar
from components.cards import feature_card
from components.metrics import dashboard_metrics

st.set_page_config(
    page_title="Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="wide"
)

# Load CSS
load_css()

# Navbar
show_navbar()

# ==========================================
# Hero Section
# ==========================================

st.title("🤝 Welcome to the Multi-Agent Negotiation Simulator")

st.markdown("""
Experience intelligent negotiations powered by AI agents.

Simulate real-world negotiations such as **Buyer vs Supplier**, **HR vs Candidate**, and **Budget Allocation**, while monitoring negotiation performance through an interactive dashboard.
""")

st.divider()

# ==========================================
# Quick Actions
# ==========================================

st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("➕ New Negotiation", width="stretch"):
        st.switch_page("pages/New_Negotiation.py")

with col2:

    if st.button("💬 Live Negotiation", width="stretch"):
        st.switch_page("pages/Live_Negotiation.py")

with col3:

    if st.button("📊 View Reports", width="stretch"):
        st.switch_page("pages/Reports.py")

st.divider()

# ==========================================
# Dashboard
# ==========================================

st.subheader("📈 Dashboard Overview")

dashboard_metrics()

st.divider()

# ==========================================
# Negotiation Scenarios
# ==========================================

st.subheader("🚀 Available Negotiation Scenarios")

col1, col2 = st.columns(2)

with col1:

    feature_card(
        "Buyer vs Supplier",
        "AI agents negotiate pricing, quantity, delivery schedules, and business terms.",
        "🛒"
    )

    st.write("")

    feature_card(
        "Budget Allocation",
        "AI agents negotiate budget distribution among departments based on priorities.",
        "💰"
    )

with col2:

    feature_card(
        "HR vs Candidate",
        "Negotiate salary, benefits, joining date, and employment terms using AI agents.",
        "💼"
    )

    st.write("")

    feature_card(
        "Custom Scenario",
        "Create your own negotiation scenario with configurable AI agents and rules.",
        "⚙️",
        "Create Scenario"
    )

st.divider()

# ==========================================
# Platform Features
# ==========================================

st.subheader("✨ Platform Features")

f1, f2, f3 = st.columns(3)

with f1:

    st.info("""
### 🤖 Intelligent AI Agents

- Buyer Agent

- Supplier Agent

- Autonomous Negotiation

- Smart Decision Making
""")

with f2:

    st.info("""
### 📊 Analytics & Reports

- Negotiation History

- Success Rate

- Performance Dashboard

- Export Reports
""")

with f3:

    st.info("""
### ⚙️ Customization

- Multiple Scenarios

- Adjustable Rounds

- Agreement Threshold

- AI Configuration
""")

st.divider()

st.caption(
    "© 2026 Multi-Agent Negotiation Simulator | Developed using Streamlit"
)