import streamlit as st

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

mode = st.session_state.get("mode", "Simulation")
role = st.session_state.get("role", None)
scenario = st.session_state.get("scenario", "Buyer vs Supplier")
max_rounds = st.session_state.get("max_rounds", 10)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# Header
# ==========================================

st.title("💬 Live Negotiation")

st.write(f"### Scenario: {scenario}")

st.divider()

chat_col, status_col = st.columns([3,1])

# ==========================================
# Chat Section
# ==========================================

with chat_col:

    st.subheader("🗨️ Negotiation Conversation")

    # ==========================
    # Simulation Mode
    # ==========================

    if mode == "Simulation":

        st.info("🤖 AI Buyer and AI Seller are negotiating automatically.")

        if st.button("▶ Start AI Negotiation", width="stretch"):

            st.session_state.messages = [

                ("Buyer AI", "We would like to purchase 500 units at $18 per unit."),

                ("Seller AI", "Our minimum acceptable price is $22 per unit."),

                ("Buyer AI", "We can increase our offer to $20 if delivery is within 10 days."),

                ("Seller AI", "Deal accepted. Delivery will be completed within 10 days.")
            ]

        for sender, message in st.session_state.messages:

            if sender == "Buyer AI":

                with st.chat_message("assistant"):
                    st.write(f"🤖 **{sender}:** {message}")

            else:

                with st.chat_message("user"):
                    st.write(f"🏭 **{sender}:** {message}")

        if len(st.session_state.messages) > 0:

            st.success("✅ Negotiation Completed Successfully")

    # ==========================
    # Practice Mode
    # ==========================

    else:

        st.info(f"🎮 Practice Mode | Your Role: **{role}**")

        if len(st.session_state.messages) == 0:

            if role == "Buyer":

                st.session_state.messages.append(
                    ("AI Seller",
                     "Welcome! Our initial quotation is $25 per unit.")
                )

            else:

                st.session_state.messages.append(
                    ("AI Buyer",
                     "Hello! We are ready to purchase at $18 per unit.")
                )

        for sender, message in st.session_state.messages:

            if sender.startswith("AI"):

                with st.chat_message("assistant"):
                    st.write(f"🤖 **{sender}:** {message}")

            else:

                with st.chat_message("user"):
                    st.write(f"🧑 **You:** {message}")

        user_offer = st.chat_input("Enter your offer...")

        if user_offer:

            st.session_state.messages.append(
                ("You", user_offer)
            )

            # Temporary AI reply
            if role == "Buyer":

                ai_reply = "Our revised offer is $23 per unit. Can you increase your price?"

            else:

                ai_reply = "We can increase our offer to $19 per unit. Please consider."

            st.session_state.messages.append(
                ("AI", ai_reply)
            )

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

    st.metric("Rounds", f"{len(st.session_state.messages)}/{max_rounds}")

    progress = min(len(st.session_state.messages) / max_rounds, 1.0)
    st.progress(progress)

    if mode == "Simulation":

        if len(st.session_state.messages) == 0:
            st.warning("Waiting to start...")

        elif len(st.session_state.messages) < 4:
            st.info("Negotiation in Progress")

        else:
            st.success("Agreement Reached")

    else:

        if len(st.session_state.messages) == 1:
            st.info("Waiting for your response")

        else:
            st.success("Negotiation Active")

st.divider()

# ==========================================
# Agreement Summary
# ==========================================

st.subheader("📄 Negotiation Summary")

if mode == "Simulation":

    if len(st.session_state.messages) >= 4:

        st.success(f"""
### Agreement Reached

**Scenario:** {scenario}

**Negotiation Mode:** {mode}

**Result:** Successful Agreement

**Final Offer:** $20 per unit

**Status:** Completed
""")

    else:

        st.info("Negotiation has not completed yet.")

else:

    st.info(f"""
### Practice Session

**Scenario:** {scenario}

**Mode:** Practice

**Role:** {role}

Continue negotiating with the AI agent until an agreement is reached.
""")

st.divider()

# ==========================================
# Navigation Buttons
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "🔄 Restart Negotiation",
        width="stretch"
    ):

        st.session_state.messages = []

        st.rerun()

with col2:

    if st.button(
        "📊 View Reports",
        width="stretch"
    ):

        st.switch_page("pages/Reports.py")

with col3:

    if st.button(
        "🏠 Back to Home",
        width="stretch"
    ):

        st.session_state.messages = []
        st.session_state.mode = None
        st.session_state.role = None

        st.switch_page("pages/Home.py")