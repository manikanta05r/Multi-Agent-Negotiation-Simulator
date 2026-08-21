import streamlit as st

# ============================================================
# LOGIN CHECK
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.switch_page("pages/Login.py")


# ============================================================
# IMPORTS
# ============================================================

from components.styles import load_css
from components.navbar import show_navbar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# STYLES + NAVBAR
# ============================================================

load_css()
show_navbar()


# ============================================================
# MAIN SECTION
# ============================================================

left, right = st.columns(
    [2, 1],
    gap="large"
)


# ============================================================
# LEFT SECTION
# ============================================================

with left:

    st.title(
        "Welcome to the Multi-Agent Negotiation Simulator"
    )

    st.write(
        "An AI-powered platform that enables intelligent "
        "agents to negotiate in real-world business scenarios."
    )

    st.subheader("Key Features")

    st.markdown(
        """
        - 🤖 AI Agent Negotiation
        - 💬 Live Negotiation Simulation
        - 📊 Interactive Dashboard
        - 📄 Automatic Report Generation
        - ⚡ Multiple Negotiation Scenarios
        """
    )

    # --------------------------------------------------------
    # START NEGOTIATION
    # --------------------------------------------------------

    if st.button(
        "🚀 Start Negotiation",
        use_container_width=True
    ):

        # app.py → Home.py
        st.switch_page(
            "pages/Home.py"
        )


# ============================================================
# RIGHT SECTION
# ============================================================

with right:

    st.info(
        """
        ### Supported Scenarios

        🛒 Buyer vs Supplier

        💼 HR vs Candidate

        💰 Budget Allocation

        ⚙️ Custom Negotiation
        """
    )


# ============================================================
# PLATFORM OVERVIEW
# ============================================================

st.divider()

st.subheader("Platform Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Negotiations",
        "0"
    )

with c2:
    st.metric(
        "Agreements",
        "0"
    )

with c3:
    st.metric(
        "AI Agents",
        "0"
    )

with c4:
    st.metric(
        "Reports",
        "0"
    )


# ============================================================
# ABOUT
# ============================================================

st.divider()

st.subheader("About")

st.write(
    """
    The Multi-Agent Negotiation Simulator enables multiple AI
    agents to negotiate under different business scenarios.

    The application consists of:

    • Streamlit Frontend

    • FastAPI Backend

    • AI Agents

    • Gemini LLM

    • Supabase Database
    """
)