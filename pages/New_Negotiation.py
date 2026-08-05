import streamlit as st
import requests

from components.styles import load_css
from components.navbar import show_navbar

st.set_page_config(
    page_title="New Negotiation",
    page_icon="🤝",
    layout="wide"
)

load_css()
show_navbar()

# ---------------- Session State ----------------

if "mode" not in st.session_state:
    st.session_state.mode = None

if "role" not in st.session_state:
    st.session_state.role = None

# ==========================================
# Header
# ==========================================

st.title("🚀 Start a New Negotiation")

st.write(
    "Select the negotiation scenario, choose the negotiation mode, configure the settings, and start negotiating."
)

st.divider()

# ==========================================
# Step 1 : Scenario
# ==========================================

st.subheader("📋 Step 1 : Select Negotiation Scenario")

scenario = st.selectbox(
    "Negotiation Scenario",
    [
        "Vendor Pricing Negotiation",
        "Job Offer Negotiation",
        "Project Budget Allocation"
    ]
)

st.divider()

# ==========================================
# Step 2 : Negotiation Mode
# ==========================================

st.subheader("🎯 Step 2 : Select Negotiation Mode")

col1, col2 = st.columns(2)

with col1:

    st.info("""
### 🤖 Simulation Mode

• AI vs AI Negotiation

• Fully Autonomous

• Observe AI Decision Making

• (Coming Soon)
""")

    if st.button(
        "🤖 Start Simulation",
        use_container_width=True
    ):
        st.session_state.mode = "Simulation"
        st.session_state.role = None

with col2:

    st.info("""
### 🎮 Practice Mode

• Human vs AI

• Role changes automatically

• Practice Real Negotiations

• Interactive Learning
""")

    if st.button(
        "🎮 Start Practice",
        use_container_width=True
    ):
        st.session_state.mode = "Practice"

# ==========================================
# Current Mode
# ==========================================

if st.session_state.mode == "Simulation":

    st.success("✅ Simulation Mode Selected")

elif st.session_state.mode == "Practice":

    st.success("✅ Practice Mode Selected")

    if scenario == "Vendor Pricing Negotiation":
        roles = ["Buyer", "Supplier"]

    elif scenario == "Job Offer Negotiation":
        roles = ["Candidate", "HR Manager"]

    elif scenario == "Project Budget Allocation":
        roles = ["Department Representative"]

    else:
        roles = ["User"]

    st.session_state.role = st.radio(
        "Your Role",
        roles,
        horizontal=True
    )

st.divider()

# ==========================================
# Step 3 : Configuration
# ==========================================

st.subheader("⚙️ Step 3 : Configuration")

left, right = st.columns(2)

with left:

    max_rounds = st.slider(
        "Maximum Rounds",
        5,
        20,
        10
    )

    agreement = st.slider(
        "Agreement Threshold (%)",
        50,
        100,
        80
    )

with right:

    response_time = st.slider(
        "AI Response Time",
        1,
        5,
        2
    )

    logging = st.checkbox(
        "Enable Logging",
        value=True
    )

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Summary")

st.write(f"**Scenario:** {scenario}")
st.write(f"**Mode:** {st.session_state.mode}")

if st.session_state.mode == "Practice":
    st.write(f"**Your Role:** {st.session_state.role}")

st.write(f"**Maximum Rounds:** {max_rounds}")
st.write(f"**Agreement Threshold:** {agreement}%")
st.write(f"**Logging:** {'Enabled' if logging else 'Disabled'}")

st.divider()

# ==========================================
# Start Negotiation
# ==========================================

if st.button(
    "🚀 Start Negotiation",
    use_container_width=True
):

    if st.session_state.mode is None:

        st.error("Please select a negotiation mode.")

    elif st.session_state.mode == "Practice" and st.session_state.role is None:

        st.error("Please choose your role.")

    else:

        backend_mode = (
            "AI vs AI"
            if st.session_state.mode == "Simulation"
            else "Human vs AI"
        )

        payload = {
            "scenario": scenario,
            "mode": backend_mode,
            "max_rounds": max_rounds
        }

        try:

            response = requests.post(
                "http://127.0.0.1:8000/start-negotiation",
                json=payload
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.session_id = data["session_id"]
                st.session_state.mode = backend_mode
                st.session_state.role = st.session_state.role
                st.session_state.scenario = scenario
                st.session_state.max_rounds = max_rounds
                st.session_state.agreement = agreement
                st.session_state.response_time = response_time
                st.session_state.logging = logging

                st.success(data["message"])

                st.switch_page("pages/Live_Negotiation.py")

            else:

                st.error(f"Backend Error: {response.text}")

        except Exception as e:

            st.error(f"Unable to connect to backend.\n\n{e}")