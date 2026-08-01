import streamlit as st
import requests

from components.styles import load_css
from components.navbar import show_navbar

st.set_page_config(
    page_title="Live Negotiation",
    page_icon="💬",
    layout="wide"
)

load_css()
show_navbar()

# ==========================================
# Session State
# ==========================================

mode = st.session_state.get("mode", "AI vs AI")
role = st.session_state.get("role", None)
scenario = st.session_state.get("scenario", "Buyer vs Supplier")
max_rounds = st.session_state.get("max_rounds", 10)
session_id = st.session_state.get("session_id", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# Header
# ==========================================

st.title("💬 Live Negotiation")

st.write(f"### Scenario: {scenario}")

st.divider()

chat_col, status_col = st.columns([3, 1])

# ==========================================
# Chat Section
# ==========================================

with chat_col:

    st.subheader("🗨️ Negotiation Conversation")

    # =====================================
    # AI vs AI
    # =====================================

    if mode == "AI vs AI":

        st.info("🤖 AI vs AI mode will be integrated later.")

    # =====================================
    # Human vs AI
    # =====================================

    else:

        st.info(f"🎮 Practice Mode | Your Role: **{role}**")

        # Show conversation
        for sender, message in st.session_state.messages:

            if sender in ["AI", "Supplier"]:

                with st.chat_message("assistant"):
                    st.write(f"🤖 **{sender}:** {message}")

            else:

                with st.chat_message("user"):
                    st.write(f"🧑 **{sender}:** {message}")

        # Chat input
        user_offer = st.chat_input("Enter your offer...")

        if user_offer:

            # Show user message
            st.session_state.messages.append(
                (role, user_offer)
            )

            try:

                response = requests.post(

                    "http://127.0.0.1:8000/next-round",

                    json={

                        "session_id": session_id,

                        "speaker": role,

                        "message": user_offer

                    }

                )

                if response.status_code == 200:

                    data = response.json()

                    # Add AI reply
                    st.session_state.messages.append(

                        (

                            data.get("speaker", "Supplier"),

                            data.get("message", "")

                        )

                    )

                    # Check negotiation status
                    if "status" in data:

                        status = data["status"]

                        if status == "agreement_reached":
                            st.success("✅ Agreement Reached")

                        elif status == "deadlock":
                            st.warning("⚠ Negotiation ended due to Deadlock")

                        elif status == "max_rounds_reached":
                            st.warning("⚠ Maximum Rounds Reached")

                else:

                    st.error(response.text)

            except Exception as e:

                st.error(f"Backend Connection Error\n\n{e}")

            st.rerun()

# ==========================================
# Status Panel
# ==========================================

with status_col:

    st.subheader("📊 Negotiation Status")

    st.metric("Mode", mode)

    if role:
        st.metric("Your Role", role)

    st.metric("Scenario", scenario)

    rounds = sum(
        1
        for sender, _ in st.session_state.messages
        if sender == role
    )

    st.metric("Rounds", f"{rounds}/{max_rounds}")

    progress = min(rounds / max_rounds, 1.0)

    st.progress(progress)

    if len(st.session_state.messages) == 0:

        st.info("Waiting to start")

    else:

        st.success("Negotiation Active")

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Negotiation Summary")

st.info(f"""
### Current Negotiation

**Scenario:** {scenario}

**Mode:** {mode}

**Role:** {role}

Continue negotiating until an agreement or deadlock is reached.
""")

st.divider()

# ==========================================
# Navigation
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("🔄 Restart Negotiation", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

with col2:

    if st.button("📊 View Reports", use_container_width=True):

        st.switch_page("pages/Reports.py")

with col3:

    if st.button("🏠 Back to Home", use_container_width=True):

        st.session_state.messages = []
        st.session_state.mode = None
        st.session_state.role = None

        st.switch_page("pages/Home.py")