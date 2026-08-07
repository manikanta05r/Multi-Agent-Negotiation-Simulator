import streamlit as st
import requests
import time

from components.styles import load_css
from components.navbar import show_navbar

st.set_page_config(
    page_title="Simulation",
    page_icon="🤖",
    layout="wide"
)

load_css()
show_navbar()

# ==========================================
# Session State
# ==========================================

scenario = st.session_state.get("scenario", "")
st.write("Scenario from session:", scenario)
mode = st.session_state.get("mode", "AI vs AI")
max_rounds = st.session_state.get("max_rounds", 10)
session_id = st.session_state.get("session_id", "")

if not session_id:
    st.error("No active negotiation found.")
    st.stop()

# ==========================================
# Speaker Icons
# ==========================================

icons = {
    "Buyer": "🛒",
    "Supplier": "🏭",
    "HR Manager": "👨‍💼",
    "Candidate": "👨‍🎓",
    "Budget Manager": "💰",
    "System": "⚙️"
}

# ==========================================
# Get Conversation
# ==========================================

try:

    response = requests.post(
        "http://127.0.0.1:8000/simulate-negotiation",
        json={"session_id": session_id}
    )

    if response.status_code != 200:
        st.error(response.text)
        st.stop()

    data = response.json()
    status = data.get("status", "running")

except Exception as e:

    st.error(f"Unable to connect to backend.\n\n{e}")
    st.stop()

conversation = data["conversation"]

print("Conversation received from backend:")
for msg in conversation:
    print(msg["speaker"], ":", msg["message"])

if scenario == "Vendor Pricing Negotiation":

    rounds = (
        sum(
            1
            for msg in conversation
            if msg["speaker"] in ["Buyer", "Supplier"]
        ) // 2
    )

elif scenario == "Job Offer Negotiation":

    rounds = (
        sum(
            1
            for msg in conversation
            if msg["speaker"] in ["Candidate", "HR Manager"]
        ) // 2
    )

elif scenario == "Project Budget Allocation":

    rounds = (
        sum(
            1
            for msg in conversation
            if msg["speaker"] == "Budget Manager"
        )
    )

else:

    rounds = 0

# ==========================================
# Header
# ==========================================

st.title("🤖 AI vs AI Negotiation")

st.write(f"### Scenario: {scenario}")

st.divider()

chat_col, status_col = st.columns([3, 1])

# ==========================================
# Chat Section
# ==========================================

with chat_col:

    st.subheader("🗨️ Negotiation Conversation")

    st.info("🤖 Simulation Mode | AI vs AI")

    chat_container = st.container()

    with chat_container:

        for msg in conversation:

            speaker = msg["speaker"]
            text = msg["message"]

            icon = icons.get(speaker, "🤖")

            # Thinking animation
            thinking = st.empty()
            thinking.info(f"{icon} {speaker} is thinking...")
            time.sleep(0.3)
            thinking.empty()

            if speaker in [
                "Supplier",
                "HR Manager",
                "Budget Manager"
            ]:

                with st.chat_message("assistant"):

                    st.write(f"{icon} **{speaker}**")
                    st.write(text)

            else:

                with st.chat_message("user"):

                    st.write(f"{icon} **{speaker}**")
                    st.write(text)

    if status == "agreement_reached":
        st.balloons()

    st.success(f"""
# ✅ AI vs AI Negotiation Completed

**Scenario:** {scenario}

**Outcome:** {status.replace("_", " ").title()}

**Rounds Completed:** {rounds}
""")

# ==========================================
# Status Panel
# ==========================================

with status_col:

    st.subheader("📊 Negotiation Status")

    st.metric("Mode", mode)

    st.metric("Scenario", scenario)

    st.metric("Rounds", f"{rounds}/{max_rounds}")

    st.progress(min(rounds / max_rounds, 1.0))

    st.divider()

    if status == "agreement_reached":

        st.success("✅ Agreement Reached")

    elif status == "deadlock":

        st.warning("⚠ Deadlock")

    elif status == "quota_exceeded":

        st.error("⛔ Gemini API Quota Exceeded")

    elif status == "max_rounds_reached":

        st.warning("⚠ Maximum Rounds Reached")

    else:

        st.info("🤖 Simulation Running")

# ==========================================
# Summary
# ==========================================

st.divider()

st.subheader("📄 Negotiation Summary")

st.info(f"""
### Negotiation Summary

**Scenario:** {scenario}

**Mode:** {mode}

**Rounds Completed:** {rounds}

**Final Status:** {status.replace("_", " ").title()}
""")

# ==========================================
# Navigation
# ==========================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("🔄 Restart Simulation", use_container_width=True):

        st.rerun()

with col2:

    if st.button("📊 View Reports", use_container_width=True):

        st.switch_page("pages/Reports.py")

with col3:

    if st.button("🏠 Back to Home", use_container_width=True):

        st.switch_page("pages/Home.py")