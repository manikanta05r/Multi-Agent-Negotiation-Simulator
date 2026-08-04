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
    "Select the negotiation mode, configure the scenario, and start the negotiation."
)

st.divider()

# ==========================================
# Step 1
# ==========================================

st.subheader("🎯 Step 1 : Select Negotiation Mode")

col1, col2 = st.columns(2)

with col1:

    st.info("""
### 🤖 Simulation Mode

• AI Buyer vs AI Seller

• Fully Autonomous Negotiation

• Observe AI Decision Making

• Best for Demonstration
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

• User vs AI

• Choose Buyer or Supplier

• Practice Negotiation

• Interactive Learning
""")

    if st.button(
        "🎮 Start Practice",
        use_container_width=True
    ):
        st.session_state.mode = "Practice"

# ---------------- Current Mode ----------------

if st.session_state.mode == "Simulation":

    st.success("✅ Simulation Mode Selected")

elif st.session_state.mode == "Practice":

    st.success("✅ Practice Mode Selected")

    st.session_state.role = st.radio(
        "Choose Your Role",
        ["Buyer", "Supplier"],
        horizontal=True
    )

st.divider()

# ==========================================
# Step 2
# ==========================================

st.subheader("📋 Step 2 : Select Scenario")

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
# Step 3
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

st.write("### Selected Configuration")

st.write(f"**Mode :** {st.session_state.mode}")

if st.session_state.mode == "Practice":
    st.write(f"**Role :** {st.session_state.role}")

st.write(f"**Scenario :** {scenario}")
st.write(f"**Maximum Rounds :** {max_rounds}")
st.write(f"**Agreement Threshold :** {agreement}%")
st.write(f"**Logging :** {'Enabled' if logging else 'Disabled'}")

st.divider()

# ==========================================
# Start Negotiation
# ==========================================

if st.button(
    "🚀 Start Negotiation",
    use_container_width=True
):

    if st.session_state.mode is None:

        st.error("Please select Simulation Mode or Practice Mode.")

    elif st.session_state.mode == "Practice" and st.session_state.role is None:

        st.error("Please choose your role.")

    else:

        # Backend accepts only these values
        backend_mode = (
            "AI vs AI"
            if st.session_state.mode == "Simulation"
            else "Human vs AI"
        )

        # Remove emojis before sending
        backend_scenario = (
            scenario.replace("🛒 ", "")
                    .replace("💼 ", "")
                    .replace("💰 ", "")
                    .replace("⚙️ ", "")
        )

        payload = {
            "scenario": backend_scenario,
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

                # Save everything for next pages
                st.session_state.session_id = data["session_id"]
                st.session_state.mode = backend_mode
                st.session_state.role = st.session_state.role
                st.session_state.scenario = backend_scenario
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