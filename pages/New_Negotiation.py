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
    "session_id": "",
    "scenario": "Vendor Pricing Negotiation",
    "max_rounds": 10,
    "agreement": 80,
    "response_time": 2,
    "logging": True,

    "agent1_config": {},
    "agent2_config": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HEADER
# ============================================================

st.title("🚀 Start a New Negotiation")

st.write(
    "Select the negotiation scenario, choose the negotiation mode, "
    "configure the agents, and start the negotiation."
)

st.divider()


# ============================================================
# STEP 1 — SCENARIO
# ============================================================

st.subheader("📋 Step 1 — Select Negotiation Scenario")

scenarios = [
    "Vendor Pricing Negotiation",
    "Job Offer Negotiation",
    "Project Budget Allocation"
]

SCENARIO_AGENTS = {
    "Vendor Pricing Negotiation": {
        "agent1_name": "Buyer",
        "agent1_role": "Buyer",
        "agent2_name": "Supplier",
        "agent2_role": "Supplier",
    },

    "Job Offer Negotiation": {
        "agent1_name": "Candidate",
        "agent1_role": "Candidate",
        "agent2_name": "HR Manager",
        "agent2_role": "HR Manager",
    },

    "Project Budget Allocation": {
        "agent1_name": "Budget Requester",
        "agent1_role": "Budget Requester",
        "agent2_name": "Budget Allocator",
        "agent2_role": "Budget Allocator",
    },
}

SCENARIO_DEFAULTS = {
    "Vendor Pricing Negotiation": {
        "agent1_starting": 95000,
        "agent1_reservation": 100000,
        "agent2_starting": 100000,
        "agent2_reservation": 95000,
    },

    "Job Offer Negotiation": {
        "agent1_starting": 1500000,
        "agent1_reservation": 1200000,
        "agent2_starting": 1000000,
        "agent2_reservation": 1200000,
    },

    "Project Budget Allocation": {
        "agent1_starting": 3000000,
        "agent1_reservation": 2400000,
        "agent2_starting": 2200000,
        "agent2_reservation": 2400000,
    }
}
scenario = st.selectbox(
    "Negotiation Scenario",
    scenarios,
    index=scenarios.index(
        st.session_state.get(
            "scenario",
            "Vendor Pricing Negotiation"
        )
    )
)


if st.session_state.get("scenario") != scenario:

    st.session_state.agent1_name = (
        SCENARIO_AGENTS[scenario]["agent1_name"]
    )

    st.session_state.agent1_role = (
        SCENARIO_AGENTS[scenario]["agent1_role"]
    )

    st.session_state.agent2_name = (
        SCENARIO_AGENTS[scenario]["agent2_name"]
    )

    st.session_state.agent2_role = (
        SCENARIO_AGENTS[scenario]["agent2_role"]
    )

    # Reset negotiation values for the selected scenario
    st.session_state.agent1_starting_target = float(
        SCENARIO_DEFAULTS[scenario]["agent1_starting"]
    )

    st.session_state.agent1_reservation_price = float(
        SCENARIO_DEFAULTS[scenario]["agent1_reservation"]
    )

    st.session_state.agent2_starting_target = float(
        SCENARIO_DEFAULTS[scenario]["agent2_starting"]
    )

    st.session_state.agent2_reservation_price = float(
        SCENARIO_DEFAULTS[scenario]["agent2_reservation"]
    )

    st.session_state.scenario = scenario


scenario_agents = SCENARIO_AGENTS[scenario]

if scenario == "Project Budget Allocation":

    project_budget = st.number_input(
        "Total Project Budget",
        min_value=0.0,
        step=100000.0,
        value=5000000.0,
        key="project_total_budget"
    )

else:

    project_budget = None


# ============================================================
# STEP 2 — NEGOTIATION MODE
# ============================================================

st.subheader("🎯 Step 2 — Select Negotiation Mode")

mode_col1, mode_col2 = st.columns(
    2,
    gap="large"
)


# ============================================================
# AI VS AI
# ============================================================

with mode_col1:

    with st.container(border=True):

        st.markdown("### 🤖 Simulation Mode")

        st.write(
            "Two autonomous AI agents negotiate with each other."
        )

        st.markdown(
            """
            - AI vs AI negotiation
            - Fully autonomous
            - Observe AI decision making
            - Automatic negotiation flow
            """
        )

        if st.button(
            "🤖 Select Simulation",
            use_container_width=True,
            key="simulation_mode"
        ):

            st.session_state.mode = "Simulation"
            st.session_state.role = None

            st.rerun()


# ============================================================
# HUMAN VS AI
# ============================================================

with mode_col2:

    with st.container(border=True):

        st.markdown("### 🎮 Practice Mode")

        st.write(
            "Practice negotiation with an AI opponent."
        )

        st.markdown(
            """
            - Human vs AI
            - Interactive negotiation
            - Choose your role
            - Practice real scenarios
            """
        )

        if st.button(
            "🎮 Select Practice",
            use_container_width=True,
            key="practice_mode"
        ):

            st.session_state.mode = "Practice"

            st.rerun()


# ============================================================
# SELECTED MODE
# ============================================================

if st.session_state.mode == "Simulation":

    st.success(
        "✅ Simulation Mode Selected — AI vs AI"
    )

elif st.session_state.mode == "Practice":

    st.success(
        "✅ Practice Mode Selected — Human vs AI"
    )


# ============================================================
# SCENARIO-SPECIFIC CONFIGURATION
# ============================================================

if scenario == "Vendor Pricing Negotiation":


    field1_label = "Starting Target"
    field2_label = "Reservation Price / Walk Away"

    field1_help = (
        "Initial price/value the agent wants to negotiate from."
    )

    field2_help = (
        "The limit beyond which the agent will walk away."
    )

    agent1_field1_default = 7000
    agent1_field2_default = 9000

    agent2_field1_default = 11000
    agent2_field2_default = 8500

    field1_prefix = "₹"
    field2_prefix = "₹"

elif scenario == "Job Offer Negotiation":

    field1_label = "Starting Salary (LPA)"
    field2_label = "Minimum / Maximum Acceptable Salary (LPA)"

    field1_help = (
        "Initial salary expectation proposed by the agent."
    )

    field2_help = (
        "Salary limit the agent is willing to accept or offer."
    )

    agent1_field1_default = 8.0
    agent1_field2_default = 6.0

    agent2_field1_default = 5.5
    agent2_field2_default = 7.0

    field1_prefix = "₹"
    field2_prefix = "₹"

else:

    field1_label = "Requested Budget (₹)"
    field2_label = "Minimum Acceptable Budget (₹)"

    field1_help = (
        "Initial budget requested by the department."
    )

    field2_help = (
        "Minimum budget required by the department."
    )

    agent1_field1_default = 1000000
    agent1_field2_default = 700000

    agent2_field1_default = 800000
    agent2_field2_default = 500000

    field1_prefix = "₹"
    field2_prefix = "₹"


    # ========================================================
    # HUMAN + AI AGENT CONFIGURATION
    # ========================================================

    config_col1, config_col2 = st.columns(2, gap="large")

    # ========================================================
    # HUMAN AGENT CONFIGURATION
    # ========================================================

    with config_col1:

        st.markdown(
            '<div class="section-title">👤 Your Agent Configuration</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):

            st.markdown(
                f"### 👤 {role}"
            )

            st.write(
                f"**Role:** {role}"
            )

            human_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Competitive",
                    "Assertive",
                    "Compromising",
                    "Flexible"
                ],
                key=f"practice_human_strategy_{scenario}_{role}"
            )

            if role == scenario_agents["agent1_role"]:

                default_human_starting = (
                    SCENARIO_DEFAULTS[scenario]["agent1_starting"]
                )

                default_human_reservation = (
                    SCENARIO_DEFAULTS[scenario]["agent1_reservation"]
                )

            else:

                default_human_starting = (
                    SCENARIO_DEFAULTS[scenario]["agent2_starting"]
                )

                default_human_reservation = (
                    SCENARIO_DEFAULTS[scenario]["agent2_reservation"]
                )

            human_starting_target = st.number_input(
                "Starting Target",
                min_value=0.0,
                step=1000.0,
                value=float(default_human_starting),
                key=f"practice_human_starting_target_{scenario}_{role}"
            )

            human_reservation_price = st.number_input(
                "Reservation Price – Walk Away",
                min_value=0.0,
                step=1000.0,
                value=float(default_human_reservation),
                key=f"practice_human_reservation_price_{scenario}_{role}"
            )

            human_instructions = st.text_area(
                "Custom Instructions",
                placeholder="Optional instructions for your negotiation...",
                height=120,
                key=f"practice_human_instructions_{scenario}_{role}"
            )


    # ========================================================
    # DETERMINE THE AI'S ROLE
    # ========================================================

    if role == scenario_agents["agent1_role"]:

        ai_agent_name = scenario_agents["agent2_name"]
        ai_agent_role = scenario_agents["agent2_role"]

        ai_starting_target = (
            SCENARIO_DEFAULTS[scenario]["agent2_starting"]
        )

        ai_reservation_price = (
            SCENARIO_DEFAULTS[scenario]["agent2_reservation"]
        )

    else:

        ai_agent_name = scenario_agents["agent1_name"]
        ai_agent_role = scenario_agents["agent1_role"]

        ai_starting_target = (
            SCENARIO_DEFAULTS[scenario]["agent1_starting"]
        )

        ai_reservation_price = (
            SCENARIO_DEFAULTS[scenario]["agent1_reservation"]
        )


    # ========================================================
    # AI AGENT CONFIGURATION
    # ========================================================

    with config_col2:

        st.markdown(
            '<div class="section-title">🤖 AI Agent Configuration</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">'
            'The AI automatically takes the opposite role from you.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):

            st.markdown(
                f"### 🤖 {ai_agent_name}"
            )

            st.write(
                f"**Role:** {ai_agent_role}"
            )

            ai_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Competitive",
                    "Assertive",
                    "Compromising",
                    "Flexible"
                ],
                key=f"practice_ai_strategy_{scenario}_{ai_agent_role}"
            )

            ai_starting_target = st.number_input(
                "Starting Target",
                min_value=0.0,
                step=1000.0,
                value=float(ai_starting_target),
                key=f"practice_ai_starting_target_{scenario}_{ai_agent_role}"
            )

            ai_reservation_price = st.number_input(
                "Reservation Price – Walk Away",
                min_value=0.0,
                step=1000.0,
                value=float(ai_reservation_price),
                key=f"practice_ai_reservation_price_{scenario}_{ai_agent_role}"
            )

            ai_instructions = st.text_area(
                "Custom Instructions",
                placeholder="Optional instructions for the AI agent...",
                height=120,
                key=f"practice_ai_instructions_{scenario}_{ai_agent_role}"
            )


    # ========================================================
    # BUILD PRACTICE AGENT CONFIGURATIONS
    # ========================================================

    if role == scenario_agents["agent1_role"]:

        human_config = {
            "name": scenario_agents["agent1_name"],
            "role": scenario_agents["agent1_role"],
            "strategy": human_strategy,
            "starting_target": float(human_starting_target),
            "reservation_price": float(human_reservation_price),
            "instructions": human_instructions
        }

        ai_config = {
            "name": ai_agent_name,
            "role": ai_agent_role,
            "strategy": ai_strategy,
            "starting_target": float(ai_starting_target),
            "reservation_price": float(ai_reservation_price),
            "instructions": ai_instructions
        }

    else:

        human_config = {
            "name": scenario_agents["agent2_name"],
            "role": scenario_agents["agent2_role"],
            "strategy": human_strategy,
            "starting_target": float(human_starting_target),
            "reservation_price": float(human_reservation_price),
            "instructions": human_instructions
        }

        ai_config = {
            "name": ai_agent_name,
            "role": ai_agent_role,
            "strategy": ai_strategy,
            "starting_target": float(ai_starting_target),
            "reservation_price": float(ai_reservation_price),
            "instructions": ai_instructions
        }


    # Store them according to the scenario's original Agent 1 / Agent 2 order
    if role == scenario_agents["agent1_role"]:

        st.session_state.agent1_config = human_config
        st.session_state.agent2_config = ai_config

    else:

        st.session_state.agent1_config = ai_config
        st.session_state.agent2_config = human_config


# ============================================================
# AI VS AI — AGENT CONFIGURATION
# ============================================================

if st.session_state.mode == "Simulation":

    st.divider()

    st.subheader("🤖 Configure AI Agents")

    st.caption(
        "Configure the two autonomous participants "
        "for the negotiation."
    )

    agent1_col, agent2_col = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # AGENT 1
    # ========================================================

    with agent1_col:

        with st.container(border=True):

            st.markdown("### 🟣 Agent 1")

            st.caption(
                "First negotiation participant"
            )

            st.divider()

            agent1_name = st.text_input(
                "Agent Name",
                value=scenario_agents["agent1_name"],
                key="agent1_name"
            )

            agent1_role = st.text_input(
                "Role",
                value=scenario_agents["agent1_role"],
                key="agent1_role"
            )

            agent1_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Assertive",
                    "Competitive",
                    "Accommodating",
                    "Compromising"
                ],
                key="agent1_strategy"
            )



            st.markdown(f"**{field1_label}**")

            if scenario == "Job Offer Negotiation":

                agent1_field1 = st.number_input(
                    field1_label,
                    min_value=0.0,
                    value=float(agent1_field1_default),
                    step=0.5,
                    format="%.1f",
                    key="agent1_field1",
                    label_visibility="collapsed"
                )

            else:

                agent1_field1 = st.number_input(
                    field1_label,
                    min_value=0,
                    value=int(agent1_field1_default),
                    step=100,
                    key="agent1_field1",
                    label_visibility="collapsed"
                )

            st.caption(field1_help)

            st.markdown(f"**{field2_label}**")

            if scenario == "Job Offer Negotiation":

                agent1_field2 = st.number_input(
                    field2_label,
                    min_value=0.0,
                    value=float(agent1_field2_default),
                    step=0.5,
                    format="%.1f",
                    key="agent1_field2",
                    label_visibility="collapsed"
                )

            else:

                agent1_field2 = st.number_input(
                    field2_label,
                    min_value=0,
                    value=int(agent1_field2_default),
                    step=100,
                    key="agent1_field2",
                    label_visibility="collapsed"
                )

            st.caption(field2_help)

            agent1_instructions = st.text_area(
                "Custom Instructions",
                placeholder="Optional instructions for Agent 1...",
                height=100,
                key="agent1_instructions"
            )


    # ========================================================
    # AGENT 2
    # ========================================================

    with agent2_col:

        with st.container(border=True):

            st.markdown("### 🟠 Agent 2")

            st.caption(
                "Second negotiation participant"
            )

            st.divider()

            agent2_name = st.text_input(
                "Agent Name",
                value=scenario_agents["agent2_name"],
                key="agent2_name"
            )

            agent2_role = st.text_input(
                "Role",
                value=scenario_agents["agent2_role"],
                key="agent2_role"
            )



            agent2_strategy = st.selectbox(
                "Negotiation Strategy",
                [
                    "Collaborative",
                    "Assertive",
                    "Competitive",
                    "Accommodating",
                    "Compromising"
                ],
                index=1,
                key="agent2_strategy"
            )



            st.markdown(f"**{field1_label}**")

            if scenario == "Job Offer Negotiation":

                agent2_field1 = st.number_input(
                    field1_label,
                    min_value=0.0,
                    value=float(agent2_field1_default),
                    step=0.5,
                    format="%.1f",
                    key="agent2_field1",
                    label_visibility="collapsed"
                )

            else:

                agent2_field1 = st.number_input(
                    field1_label,
                    min_value=0,
                    value=int(agent2_field1_default),
                    step=100,
                    key="agent2_field1",
                    label_visibility="collapsed"
                )

            st.caption(field1_help)

            st.markdown(f"**{field2_label}**")

            if scenario == "Job Offer Negotiation":

                agent2_field2 = st.number_input(
                    field2_label,
                    min_value=0.0,
                    value=float(agent2_field2_default),
                    step=0.5,
                    format="%.1f",
                    key="agent2_field2",
                    label_visibility="collapsed"
                )

            else:

                agent2_field2 = st.number_input(
                    field2_label,
                    min_value=0,
                    value=int(agent2_field2_default),
                    step=100,
                    key="agent2_field2",
                    label_visibility="collapsed"
                )

            st.caption(field2_help)

            agent2_starting_target = st.number_input(
                "Starting Target",
                min_value=0.0,
                step=1000.0,
                value=float(
                    SCENARIO_DEFAULTS[scenario]["agent2_starting"]
                ),
                key="agent2_starting_target"
            )

            agent2_reservation_price = st.number_input(
                "Reservation Price – Walk Away",
                min_value=0.0,
                step=1000.0,
                value=float(
                    SCENARIO_DEFAULTS[scenario]["agent2_reservation"]
                ),
                key="agent2_reservation_price"
            )


            agent2_instructions = st.text_area(
                "Custom Instructions",
                placeholder=(
                    "Optional instructions for Agent 2..."
                ),
                height=100,
                key="agent2_instructions"
            )



# ============================================================
# PRACTICE MODE — ROLE
# ============================================================

elif st.session_state.mode == "Practice":

    st.divider()

    st.subheader("👤 Choose Your Role")

    if scenario == "Vendor Pricing Negotiation":

        roles = [
            "Buyer",
            "Supplier"
        ]

    elif scenario == "Job Offer Negotiation":

        roles = [
            "Candidate",
            "HR Manager"
        ]

    else:

        roles = [
            "Department Representative"
        ]

    st.session_state.role = st.radio(
        "Your Role",
        roles,
        horizontal=True
    )

    st.session_state.agent1_config = {
        "name": agent1_name,
        "role": agent1_role,
        "strategy": agent1_strategy,
        "scenario": scenario,
        "starting_target": agent1_field1,
        "reservation_price": agent1_field2,
        "instructions": agent1_instructions
    }

    st.session_state.agent2_config = {
        "name": agent2_name,
        "role": agent2_role,
        "strategy": agent2_strategy,
        "scenario": scenario,
        "starting_target": agent2_field1,
        "reservation_price": agent2_field2,
        "instructions": agent2_instructions
    }

# ============================================================
# STEP 3 — CONFIGURATION
# ============================================================

st.divider()

st.subheader("⚙️ Step 3 — Configuration")

config_left, config_right = st.columns(
    2,
    gap="large"
)

with config_left:

    max_rounds = st.slider(
        "Maximum Rounds",
        min_value=5,
        max_value=20,
        value=st.session_state.max_rounds
    )

    agreement = st.slider(
        "Agreement Threshold (%)",
        min_value=50,
        max_value=100,
        value=st.session_state.agreement
    )


with config_right:

    response_time = st.slider(
        "AI Response Time",
        min_value=1,
        max_value=5,
        value=st.session_state.response_time
    )

    logging = st.checkbox(
        "Enable Logging",
        value=st.session_state.logging
    )


# ============================================================
# SUMMARY
# ============================================================

st.divider()

st.subheader("📄 Negotiation Summary")

summary1, summary2, summary3, summary4 = st.columns(4)

with summary1:

    st.caption("Scenario")

    st.write(scenario)


with summary2:

    st.caption("Mode")

    st.write(
        st.session_state.mode
        if st.session_state.mode
        else "Not Selected"
    )


with summary3:

    st.caption("Maximum Rounds")

    st.write(max_rounds)


with summary4:

    st.caption("Participants")

    if st.session_state.mode == "Simulation":

        st.write("AI Agents")

    elif st.session_state.mode == "Practice":

        st.write("Human + AI")

    else:

        st.write("Not Selected")


# ============================================================
# AI AGENT SUMMARY
# ============================================================

if st.session_state.mode == "Simulation":

    st.divider()

    st.subheader("🤖 Agent Configuration Summary")

    summary_agent1, summary_agent2 = st.columns(
        2,
        gap="large"
    )

    with summary_agent1:

        with st.container(border=True):

            st.markdown(
                f"### 🟣 {agent1_name}"
            )

            st.write(
                f"**Role:** {agent1_role}"
            )

            st.write(
                f"**Strategy:** {agent1_strategy}"
            )

            st.write(
                f"**{field1_label}:** {agent1_field1}"
            )

            st.write(
                f"**{field2_label}:** {agent1_field2}"
            )


    with summary_agent2:

        with st.container(border=True):

            st.markdown(
                f"### 🟠 {agent2_name}"
            )

            st.write(
                f"**Role:** {agent2_role}"
            )

            st.write(
                f"**Strategy:** {agent2_strategy}"
            )

            st.write(
                f"**{field1_label}:** {agent2_field1}"
            )

            st.write(
                f"**{field2_label}:** {agent2_field2}"
            )


# ============================================================
# START NEGOTIATION
# ============================================================

st.divider()

if st.button(
    "🚀 Start Negotiation",
    use_container_width=True,
    type="primary"
):

    # --------------------------------------------------------
    # MODE VALIDATION
    # --------------------------------------------------------

    if st.session_state.mode is None:

        st.error(
            "Please select a negotiation mode."
        )

        st.stop()


    if (
        st.session_state.mode == "Practice"
        and st.session_state.role is None
    ):

        st.error(
            "Please choose your role."
        )

        st.stop()


    # ========================================================
    # SAVE AI AGENT CONFIGURATION
    # ========================================================

    if st.session_state.mode == "Simulation":

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if agent1_field1 <= 0 or agent1_field2 <= 0:

            st.error(
                "Agent 1 values must be greater than 0."
            )

            st.stop()


        if agent2_field1 <= 0 or agent2_field2 <= 0:

            st.error(
                "Agent 2 values must be greater than 0."
            )

            st.stop()


        # ----------------------------------------------------
        # VENDOR PRICING VALIDATION
        # ----------------------------------------------------

        if scenario == "Vendor Pricing Negotiation":

            # Buyer:
            # Starting target < Walk-away maximum

            if agent1_field1 >= agent1_field2:

                st.error(
                    "Agent 1: Starting Target should be "
                    "less than the Reservation Price / Walk Away."
                )

                st.stop()


            # Supplier:
            # Starting target > Walk-away minimum

            if agent2_field1 <= agent2_field2:

                st.error(
                    "Agent 2: Starting Target should be "
                    "greater than the Reservation Price / Walk Away."
                )

                st.stop()


        # ----------------------------------------------------
        # JOB OFFER VALIDATION
        # ----------------------------------------------------

        elif scenario == "Job Offer Negotiation":

            # Candidate:
            # Starting expectation should be >= minimum

            if agent1_field1 < agent1_field2:

                st.error(
                    "Agent 1: Starting Salary should be "
                    "greater than or equal to the Minimum Acceptable Salary."
                )

                st.stop()


            # HR:
            # Starting offer should be <= maximum budget

            if agent2_field1 > agent2_field2:

                st.error(
                    "Agent 2: Starting Salary should be "
                    "less than or equal to the Maximum Acceptable Salary."
                )

                st.stop()


        # ----------------------------------------------------
        # PROJECT BUDGET VALIDATION
        # ----------------------------------------------------

        elif scenario == "Project Budget Allocation":

            # Requested budget should be >= minimum

            if agent1_field1 < agent1_field2:

                st.error(
                    "Agent 1: Requested Budget should be "
                    "greater than or equal to Minimum Acceptable Budget."
                )

                st.stop()


            if agent2_field1 < agent2_field2:

                st.error(
                    "Agent 2: Requested Budget should be "
                    "greater than or equal to Minimum Acceptable Budget."
                )

                st.stop()


        # ----------------------------------------------------
        # STORE AGENT 1
        # ----------------------------------------------------

        st.session_state.agent1_config = {
            "name": agent1_name,
            "role": agent1_role,
            "strategy": agent1_strategy,
            "scenario": scenario,
            "starting_target": agent1_field1,
            "reservation_price": agent1_field2,
            "instructions": agent1_instructions

        }


        # ----------------------------------------------------
        # STORE AGENT 2
        # ----------------------------------------------------

        st.session_state.agent2_config = {
            "name": agent2_name,
            "role": agent2_role,
            "strategy": agent2_strategy,
            "scenario": scenario,
            "starting_target": agent2_field1,
            "reservation_price": agent2_field2,
            "instructions": agent2_instructions
        }


    # ========================================================
    # BACKEND MODE
    # ========================================================

    backend_mode = (
        "AI vs AI"
        if st.session_state.mode == "Simulation"
        else "Human vs AI"
    )


    # ========================================================
    # BASE PAYLOAD
    # ========================================================

    payload = {

        "scenario": scenario,

        "mode": backend_mode,

        "max_rounds": max_rounds,

        "agreement_threshold": agreement,

        "response_time": response_time,

        "logging": logging
    }


    # ========================================================
    # AI VS AI PAYLOAD
    # ========================================================

    if st.session_state.mode == "Simulation":

        payload["agent1"] = (
            st.session_state.agent1_config
        )

        payload["agent2"] = (
            st.session_state.agent2_config
        )


    # ========================================================
    # HUMAN VS AI PAYLOAD
    # ========================================================

    elif st.session_state.mode == "Practice":

        payload["role"] = (
            st.session_state.role
        )


    # ========================================================
    # START BACKEND SESSION
    # ========================================================

    try:

        with st.spinner(
            "Starting negotiation..."
        ):

            response = requests.post(
                "http://127.0.0.1:8000/start-negotiation",
                json=payload,
                timeout=15
            )


        if response.status_code == 200:

            data = response.json()

            st.session_state.session_id = data.get(
                "session_id",
                ""
            )

            st.session_state.mode = backend_mode

            st.session_state.scenario = scenario

            st.session_state.max_rounds = max_rounds

            st.session_state.agreement = agreement

            st.session_state.response_time = response_time

            st.session_state.logging = logging


            st.success(
                data.get(
                    "message",
                    "Negotiation started successfully."
                )
            )


            # ------------------------------------------------
            # AI VS AI
            # ------------------------------------------------

            if backend_mode == "AI vs AI":

                st.session_state.simulation_messages = []

                st.session_state.simulation_round = 0

                st.session_state.simulation_status = (
                    "Waiting"
                )

                st.session_state.active_agent = None

                st.session_state.simulation_finished = False

                st.switch_page(
                    "pages/Simulation.py"
                )


            # ------------------------------------------------
            # HUMAN VS AI
            # ------------------------------------------------

            else:

                st.session_state.messages = []

                st.switch_page(
                    "pages/Live_Negotiation.py"
                )


        else:

            st.error(
                f"Backend Error: {response.text}"
            )


    except requests.exceptions.RequestException as e:

        st.error(
            "Unable to connect to backend.\n\n"
            f"{e}"
        )
