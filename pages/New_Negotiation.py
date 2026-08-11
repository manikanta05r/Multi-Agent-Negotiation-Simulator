import streamlit as st
import requests

from components.styles import load_css
from components.navbar import show_navbar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="New Negotiation",
    page_icon="🤝",
    layout="wide"
)

load_css()
show_navbar()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "mode": None,
    "role": None,
    "scenario": "Vendor Pricing Negotiation",
    "session_id": "",
    "max_rounds": 10,
    "agreement": 80,
    "response_time": 2,
    "logging": True,

    # AI Agent configuration
    "agent1_config": {},
    "agent2_config": {},

    # Simulation state
    "simulation_messages": [],
    "simulation_started": False,
    "simulation_finished": False,
    "simulation_round": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM UI CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #667085;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .section-description {
        color: #667085;
        margin-bottom: 18px;
    }

    .mode-card {
        padding: 24px;
        border: 1px solid #e4e7ec;
        border-radius: 16px;
        background: #ffffff;
        min-height: 220px;
    }

    .mode-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .mode-title {
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .mode-description {
        color: #667085;
        line-height: 1.7;
        min-height: 110px;
    }

    .agent-header {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 3px;
    }

    .agent-subtitle {
        color: #667085;
        margin-bottom: 20px;
    }

    .summary-box {
        padding: 20px;
        border: 1px solid #e4e7ec;
        border-radius: 14px;
        background: #ffffff;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚀 Start a New Negotiation</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Select the scenario, choose the negotiation mode, configure the participants, '
    'and start the negotiation.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# STEP 1 — SCENARIO
# ============================================================

st.markdown(
    '<div class="section-title">📋 Step 1 — Select Negotiation Scenario</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Choose the type of negotiation you want to practice or simulate.'
    '</div>',
    unsafe_allow_html=True
)

scenario = st.selectbox(
    "Negotiation Scenario",
    [
        "Vendor Pricing Negotiation",
        "Job Offer Negotiation",
        "Project Budget Allocation"
    ],
    key="scenario_select"
)

st.session_state.scenario = scenario

st.divider()


# ============================================================
# STEP 2 — MODE
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Step 2 — Select Negotiation Mode</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Choose whether you want two AI agents to negotiate or participate yourself.'
    '</div>',
    unsafe_allow_html=True
)

mode_col1, mode_col2 = st.columns(2, gap="large")


# ---------------- SIMULATION ----------------

with mode_col1:

    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-icon">🤖</div>
            <div class="mode-title">Simulation Mode</div>
            <div class="mode-description">
                <b>AI vs AI Negotiation</b><br>
                • Two autonomous agents<br>
                • Watch their negotiation strategies<br>
                • Observe offers and counter-offers<br>
                • Analyze the final outcome
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🤖 Select AI vs AI",
        use_container_width=True,
        key="simulation_mode_button"
    ):
        st.session_state.mode = "Simulation"
        st.session_state.role = None
        st.rerun()


# ---------------- PRACTICE ----------------

with mode_col2:

    st.markdown(
        """
        <div class="mode-card">
            <div class="mode-icon">🎮</div>
            <div class="mode-title">Practice Mode</div>
            <div class="mode-description">
                <b>Human vs AI Negotiation</b><br>
                • You control one participant<br>
                • AI responds to your offers<br>
                • Practice realistic negotiations<br>
                • Improve your negotiation skills
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🎮 Select Human vs AI",
        use_container_width=True,
        key="practice_mode_button"
    ):
        st.session_state.mode = "Practice"
        st.rerun()


# ============================================================
# CURRENT MODE
# ============================================================

if st.session_state.mode == "Simulation":

    st.success("🤖 Simulation Mode Selected — AI vs AI")

elif st.session_state.mode == "Practice":

    st.info("🎮 Practice Mode Selected — Human vs AI")


# ============================================================
# PRACTICE ROLE
# ============================================================

if st.session_state.mode == "Practice":

    st.divider()

    st.markdown(
        '<div class="section-title">👤 Choose Your Role</div>',
        unsafe_allow_html=True
    )

    if scenario == "Vendor Pricing Negotiation":
        roles = ["Buyer", "Supplier"]

    elif scenario == "Job Offer Negotiation":
        roles = ["Candidate", "HR Manager"]

    else:
        roles = ["Department Representative"]

    role = st.radio(
        "Your Role",
        roles,
        horizontal=True,
        key="practice_role"
    )

    st.session_state.role = role


# ============================================================
# AI AGENTS — SIMULATION ONLY
# ============================================================

if st.session_state.mode == "Simulation":

    st.divider()

    st.markdown(
        '<div class="section-title">🤖 Configure AI Agents</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Configure the two autonomous participants in the simulation.'
        '</div>',
        unsafe_allow_html=True
    )

    agent_col1, agent_col2 = st.columns(2, gap="large")


    # ========================================================
    # AGENT 1
    # ========================================================

    with agent_col1:

        with st.container(border=True):

            st.markdown(
                '<div class="agent-header">🟣 Agent 1</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="agent-subtitle">'
                'First negotiation participant'
                '</div>',
                unsafe_allow_html=True
            )

            agent1_name = st.text_input(
                "Agent Name",
                value="Buyer",
                key="agent1_name"
            )

            agent1_role = st.text_input(
                "Role",
                value="Buyer",
                key="agent1_role"
            )

            agent1_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Competitive",
                    "Assertive",
                    "Compromising",
                    "Flexible"
                ],
                key="agent1_strategy"
            )

            agent1_instructions = st.text_area(
                "Custom Instructions",
                placeholder="Optional instructions for Agent 1...",
                height=120,
                key="agent1_instructions"
            )


    # ========================================================
    # AGENT 2
    # ========================================================

    with agent_col2:

        with st.container(border=True):

            st.markdown(
                '<div class="agent-header">🟠 Agent 2</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="agent-subtitle">'
                'Second negotiation participant'
                '</div>',
                unsafe_allow_html=True
            )

            agent2_name = st.text_input(
                "Agent Name",
                value="Supplier",
                key="agent2_name"
            )

            agent2_role = st.text_input(
                "Role",
                value="Supplier",
                key="agent2_role"
            )

            agent2_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Competitive",
                    "Assertive",
                    "Compromising",
                    "Flexible"
                ],
                key="agent2_strategy"
            )

            agent2_instructions = st.text_area(
                "Custom Instructions",
                placeholder="Optional instructions for Agent 2...",
                height=120,
                key="agent2_instructions"
            )

    # Store configuration safely
    st.session_state.agent1_config = {
        "name": agent1_name,
        "role": agent1_role,
        "strategy": agent1_strategy,
        "instructions": agent1_instructions
    }

    st.session_state.agent2_config = {
        "name": agent2_name,
        "role": agent2_role,
        "strategy": agent2_strategy,
        "instructions": agent2_instructions
    }


# ============================================================
# STEP 3 — CONFIGURATION
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">⚙️ Step 3 — Configuration</div>',
    unsafe_allow_html=True
)

config_left, config_right = st.columns(2, gap="large")


with config_left:

    max_rounds = st.slider(
        "Maximum Rounds",
        min_value=5,
        max_value=20,
        value=10,
        key="max_rounds_slider"
    )

    agreement = st.slider(
        "Agreement Threshold (%)",
        min_value=50,
        max_value=100,
        value=80,
        key="agreement_slider"
    )


with config_right:

    response_time = st.slider(
        "AI Response Time",
        min_value=1,
        max_value=5,
        value=2,
        key="response_time_slider"
    )

    logging = st.checkbox(
        "Enable Logging",
        value=True,
        key="logging_checkbox"
    )


# ============================================================
# SUMMARY
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📄 Negotiation Summary</div>',
    unsafe_allow_html=True
)

summary1, summary2, summary3, summary4 = st.columns(4, gap="medium")

with summary1:
    st.metric("Scenario", scenario)

with summary2:
    display_mode = (
        "AI vs AI"
        if st.session_state.mode == "Simulation"
        else "Human vs AI"
        if st.session_state.mode == "Practice"
        else "Not Selected"
    )
    st.metric("Mode", display_mode)

with summary3:
    st.metric("Rounds", max_rounds)

with summary4:
    if st.session_state.mode == "Practice":
        st.metric("Your Role", st.session_state.role)
    elif st.session_state.mode == "Simulation":
        st.metric("Participants", "2 AI Agents")
    else:
        st.metric("Participants", "—")


# ============================================================
# START NEGOTIATION
# ============================================================

st.divider()

if st.button(
    "🚀 Start Negotiation",
    use_container_width=True,
    type="primary",
    key="start_negotiation"
):

    if st.session_state.mode is None:

        st.error("Please select a negotiation mode first.")

    elif (
        st.session_state.mode == "Practice"
        and st.session_state.role is None
    ):

        st.error("Please select your role.")

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
                json=payload,
                timeout=30
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.session_id = data.get(
                    "session_id",
                    ""
                )

                st.session_state.max_rounds = max_rounds
                st.session_state.agreement = agreement
                st.session_state.response_time = response_time
                st.session_state.logging = logging

                # Reset simulation
                st.session_state.simulation_messages = []
                st.session_state.simulation_started = False
                st.session_state.simulation_finished = False
                st.session_state.simulation_round = 0

                if backend_mode == "AI vs AI":

                    st.session_state.mode = "AI vs AI"

                    st.switch_page(
                        "pages/Simulation.py"
                    )

                else:

                    st.session_state.mode = "Human vs AI"

                    st.switch_page(
                        "pages/Live_Negotiation.py"
                    )

            else:

                st.error(
                    f"Backend Error: {response.text}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Backend is not running. "
                "Start FastAPI first."
            )

        except Exception as e:

            st.error(
                f"❌ Unable to start negotiation:\n\n{e}"
            )