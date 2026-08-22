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
# Page-level style additions — reconciled with
# the site's global style.css (Poppins, navy
# sidebar, blue-mint gradient). Only styles
# elements not already covered globally
# (hero copy, st.info feature panels, section
# spacing). No logic or component calls touched.
# ==========================================

st.markdown(
    """
    <style>

    :root {
        --brand-navy: #0f172a;
        --brand-blue: #1e3a8a;
        --brand-gradient-start: #93c5fd;
        --brand-gradient-end: #a7f3d0;
        --brand-muted: #475569;
        --brand-border: #e2e8f0;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    /* ---- Hero intro paragraph under the title ---- */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        color: var(--brand-muted);
        line-height: 1.7;
    }

    /* ---- Subheaders ("Quick Actions", "Dashboard Overview", etc.) ---- */
    div[data-testid="stMarkdownContainer"] h3 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---- Info panels (Platform Features column) styled as elevated cards ---- */
    div[data-testid="stAlert"] {
        background: #ffffff !important;
        border: 1px solid var(--brand-border) !important;
        border-left: 4px solid var(--brand-gradient-start) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        padding: 1.25rem 1.5rem !important;
    }

    div[data-testid="stAlert"] p {
        color: var(--brand-navy) !important;
    }

    div[data-testid="stAlert"] li {
        color: var(--brand-muted) !important;
        margin-bottom: 0.25rem;
    }

    div[data-testid="stAlert"] h3 {
        color: var(--brand-blue) !important;
        margin-bottom: 0.75rem !important;
    }

    /* ---- Footer caption ---- */
    div[data-testid="stCaptionContainer"] {
        text-align: center;
        color: var(--brand-muted) !important;
        font-size: 12px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

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

# ------------------------------------------
# Maps each scenario card to the exact
# SCENARIOS entry used in New_Negotiation.py,
# so the dropdown there pre-selects correctly
# and SCENARIO_AGENTS / SCENARIO_DEFAULTS
# auto-populate for that scenario.
# ------------------------------------------

col1, col2 = st.columns(2)

with col1:

    if feature_card(
        "Buyer vs Supplier",
        "AI agents negotiate pricing, quantity, delivery schedules, and business terms.",
        "🛒"
    ):

        st.session_state.scenario = "Vendor Pricing Negotiation"
        st.session_state.scenario_selector = "Vendor Pricing Negotiation"

        st.switch_page("pages/New_Negotiation.py")

    st.write("")

    if feature_card(
        "Budget Allocation",
        "AI agents negotiate budget distribution among departments based on priorities.",
        "💰"
    ):

        st.session_state.scenario = "Project Budget Allocation"
        st.session_state.scenario_selector = "Project Budget Allocation"

        st.switch_page("pages/New_Negotiation.py")

with col2:

    if feature_card(
        "HR vs Candidate",
        "Negotiate salary, benefits, joining date, and employment terms using AI agents.",
        "💼"
    ):

        st.session_state.scenario = "Job Offer Negotiation"
        st.session_state.scenario_selector = "Job Offer Negotiation"

        st.switch_page("pages/New_Negotiation.py")

    st.write("")

    if feature_card(
        "Custom Scenario",
        "Create your own negotiation scenario with configurable AI agents and rules.",
        "⚙️",
        "Create Scenario"
    ):

        # No scenario forced here — leave whatever is
        # already in session state so the user can pick
        # freely from the dropdown on the next page.
        st.switch_page("pages/Live_Negotiation.py")

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