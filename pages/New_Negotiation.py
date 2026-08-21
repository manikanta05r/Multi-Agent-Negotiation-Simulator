import streamlit as st
import requests


# ============================================================
# HELPERS
# ============================================================

def format_inr(value):
    """Format numbers using Indian comma grouping."""
    try:
        amount = int(round(float(value)))
    except (TypeError, ValueError):
        return str(value)

    sign = "-" if amount < 0 else ""
    digits = str(abs(amount))

    if len(digits) <= 3:
        return f"{sign}₹{digits}"

    last_three = digits[-3:]
    rest = digits[:-3]

    groups = []

    while rest:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]

    return f"{sign}₹{','.join(groups + [last_three])}"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="New Negotiation",
    page_icon="🤝",
    layout="wide",
)

from components.styles import load_css
from components.navbar import show_navbar

load_css()
show_navbar()


# ============================================================
# SESSION STATE DEFAULTS
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

    "agent1_name": "Buyer",
    "agent1_role": "Buyer",
    "agent1_strategy": "Collaborative",
    "agent1_instructions": "",

    "agent2_name": "Supplier",
    "agent2_role": "Supplier",
    "agent2_strategy": "Assertive",
    "agent2_instructions": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SCENARIOS
# ============================================================

SCENARIOS = [
    "Vendor Pricing Negotiation",
    "Job Offer Negotiation",
    "Project Budget Allocation",
]


# ============================================================
# SCENARIO AGENTS
# ============================================================

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


# ============================================================
# SCENARIO DEFAULT VALUES
# ============================================================

SCENARIO_DEFAULTS = {

    "Vendor Pricing Negotiation": {
        "agent1_starting": 90000,
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
    },
}


# ============================================================
# STRATEGIES
# ============================================================

STRATEGIES = [
    "Collaborative",
    "Assertive",
    "Competitive",
    "Compromising",
    "Flexible",
]


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

current_scenario = st.session_state.get(
    "scenario",
    "Vendor Pricing Negotiation",
)

if current_scenario not in SCENARIOS:
    current_scenario = "Vendor Pricing Negotiation"


scenario = st.selectbox(
    "Negotiation Scenario",
    SCENARIOS,
    index=SCENARIOS.index(current_scenario),
    key="scenario_selector",
)


# ============================================================
# SCENARIO DATA
# ============================================================

scenario_agents = SCENARIO_AGENTS[scenario]

scenario_defaults = SCENARIO_DEFAULTS[scenario]


# ============================================================
# APPLY SCENARIO DEFAULTS WHEN SCENARIO CHANGES
# ============================================================

if st.session_state.get("scenario") != scenario:

    # --------------------------------------------------------
    # RESET AGENT NAMES
    # --------------------------------------------------------

    st.session_state.agent1_name = (
        scenario_agents["agent1_name"]
    )

    st.session_state.agent1_role = (
        scenario_agents["agent1_role"]
    )

    st.session_state.agent2_name = (
        scenario_agents["agent2_name"]
    )

    st.session_state.agent2_role = (
        scenario_agents["agent2_role"]
    )

    # --------------------------------------------------------
    # RESET AGENT CONFIG
    # --------------------------------------------------------

    st.session_state.agent1_config = {}
    st.session_state.agent2_config = {}

    # --------------------------------------------------------
    # RESET STRATEGIES
    # --------------------------------------------------------

    st.session_state.agent1_strategy = "Collaborative"
    st.session_state.agent2_strategy = "Assertive"

    # --------------------------------------------------------
    # RESET INSTRUCTIONS
    # --------------------------------------------------------

    st.session_state.agent1_instructions = ""
    st.session_state.agent2_instructions = ""

    # --------------------------------------------------------
    # RESET TARGET VALUES
    # --------------------------------------------------------

    st.session_state.agent1_starting_target = float(
        scenario_defaults["agent1_starting"]
    )

    st.session_state.agent1_reservation_price = float(
        scenario_defaults["agent1_reservation"]
    )

    st.session_state.agent2_starting_target = float(
        scenario_defaults["agent2_starting"]
    )

    st.session_state.agent2_reservation_price = float(
        scenario_defaults["agent2_reservation"]
    )

    # --------------------------------------------------------
    # SAVE SCENARIO
    # --------------------------------------------------------

    st.session_state.scenario = scenario

    st.rerun()


# ============================================================
# PROJECT BUDGET
# ============================================================

if scenario == "Project Budget Allocation":

    project_budget = st.number_input(
        "Total Project Budget",
        min_value=0.0,
        step=100000.0,
        value=5000000.0,
        key="project_total_budget",
    )

else:

    project_budget = None


# ============================================================
# FIELD LABELS
# ============================================================

if scenario == "Vendor Pricing Negotiation":

    field1_label = "Starting Target"

    field2_label = (
        "Reservation Price / Walk Away"
    )

    field1_help = (
        "Initial price/value the agent wants to negotiate from."
    )

    field2_help = (
        "The hard limit beyond which the agent will walk away."
    )


elif scenario == "Job Offer Negotiation":

    field1_label = "Starting Salary (₹)"

    field2_label = (
        "Reservation Salary / Walk Away (₹)"
    )

    field1_help = (
        "Initial salary position used to start the negotiation."
    )

    field2_help = (
        "The hard salary boundary the agent will not cross."
    )


else:

    field1_label = (
        "Starting Budget Position (₹)"
    )

    field2_label = (
        "Minimum Acceptable Budget / Walk-Away (₹)"
    )

    field1_help = (
        "The amount this agent must use as its opening "
        "negotiation position. The AI must NOT start from "
        "the Total Project Budget."
    )

    field2_help = (
        "The absolute negotiation boundary. The agent must "
        "never accept a value below this amount."
    )


agent1_field1_default = scenario_defaults[
    "agent1_starting"
]

agent1_field2_default = scenario_defaults[
    "agent1_reservation"
]

agent2_field1_default = scenario_defaults[
    "agent2_starting"
]

agent2_field2_default = scenario_defaults[
    "agent2_reservation"
]


# ============================================================
# STEP 2 — MODE
# ============================================================

st.subheader("🎯 Step 2 — Select Negotiation Mode")

mode_col1, mode_col2 = st.columns(
    2,
    gap="large",
)


# ============================================================
# AI VS AI
# ============================================================

with mode_col1:

    with st.container(border=True):

        st.markdown(
            "### 🤖 Simulation Mode"
        )

        st.write(
            "Two autonomous AI agents negotiate with each other."
        )

        st.markdown(
            """
            - AI vs AI negotiation
            - Fully autonomous
            - Zig-zag turn-by-turn conversation
            - Automatic negotiation flow
            """
        )

        if st.button(
            "🤖 Select Simulation",
            width="stretch",
            key="simulation_mode",
        ):

            st.session_state.mode = "Simulation"

            st.session_state.role = None

            st.rerun()


# ============================================================
# HUMAN VS AI
# ============================================================

with mode_col2:

    with st.container(border=True):

        st.markdown(
            "### 🎮 Practice Mode"
        )

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
            width="stretch",
            key="practice_mode",
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
# PRACTICE MODE
# ============================================================

if st.session_state.mode == "Practice":

    st.divider()

    st.subheader(
        "👤 Choose Your Role"
    )

    if scenario == "Vendor Pricing Negotiation":

        roles = [
            "Buyer",
            "Supplier",
        ]

    elif scenario == "Job Offer Negotiation":

        roles = [
            "Candidate",
            "HR Manager",
        ]

    else:

        roles = [
            "Budget Requester",
            "Budget Allocator",
        ]

    role = st.radio(
        "Your Role",
        roles,
        horizontal=True,
        key=f"practice_role_{scenario}",
    )

    st.session_state.role = role

    config_col1, config_col2 = st.columns(
        2,
        gap="large",
    )

    # ========================================================
    # HUMAN
    # ========================================================

    with config_col1:

        st.markdown(
            "### 👤 Your Agent Configuration"
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
                STRATEGIES,
                key=(
                    f"practice_human_strategy_"
                    f"{scenario}_{role}"
                ),
            )

            if (
                role
                == scenario_agents["agent1_role"]
            ):

                default_human_starting = (
                    scenario_defaults["agent1_starting"]
                )

                default_human_reservation = (
                    scenario_defaults["agent1_reservation"]
                )

            else:

                default_human_starting = (
                    scenario_defaults["agent2_starting"]
                )

                default_human_reservation = (
                    scenario_defaults["agent2_reservation"]
                )

            human_starting_target = st.number_input(
                field1_label,
                min_value=0.0,
                step=1000.0,
                value=float(
                    default_human_starting
                ),
                key=(
                    f"practice_human_starting_"
                    f"{scenario}_{role}"
                ),
            )

            human_reservation_price = st.number_input(
                field2_label,
                min_value=0.0,
                step=1000.0,
                value=float(
                    default_human_reservation
                ),
                key=(
                    f"practice_human_reservation_"
                    f"{scenario}_{role}"
                ),
            )

            st.caption(
                f"Amount: {format_inr(human_starting_target)}"
            )

            st.caption(
                field1_help
            )

            st.caption(
                f"Amount: {format_inr(human_reservation_price)}"
            )

            st.caption(
                field2_help
            )

            human_instructions = st.text_area(
                "Custom Instructions",
                placeholder=(
                    "Optional instructions for your negotiation..."
                ),
                height=120,
                key=(
                    f"practice_human_instructions_"
                    f"{scenario}_{role}"
                ),
            )

    # ========================================================
    # AI ROLE
    # ========================================================

    if (
        role
        == scenario_agents["agent1_role"]
    ):

        ai_agent_name = (
            scenario_agents["agent2_name"]
        )

        ai_agent_role = (
            scenario_agents["agent2_role"]
        )

        ai_default_starting = (
            scenario_defaults["agent2_starting"]
        )

        ai_default_reservation = (
            scenario_defaults["agent2_reservation"]
        )

    else:

        ai_agent_name = (
            scenario_agents["agent1_name"]
        )

        ai_agent_role = (
            scenario_agents["agent1_role"]
        )

        ai_default_starting = (
            scenario_defaults["agent1_starting"]
        )

        ai_default_reservation = (
            scenario_defaults["agent1_reservation"]
        )

    # ========================================================
    # AI
    # ========================================================

    with config_col2:

        st.markdown(
            "### 🤖 AI Agent Configuration"
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
                STRATEGIES,
                key=(
                    f"practice_ai_strategy_"
                    f"{scenario}_{ai_agent_role}"
                ),
            )

            ai_starting_target = st.number_input(
                field1_label,
                min_value=0.0,
                step=1000.0,
                value=float(
                    ai_default_starting
                ),
                key=(
                    f"practice_ai_starting_"
                    f"{scenario}_{ai_agent_role}"
                ),
            )

            ai_reservation_price = st.number_input(
                field2_label,
                min_value=0.0,
                step=1000.0,
                value=float(
                    ai_default_reservation
                ),
                key=(
                    f"practice_ai_reservation_"
                    f"{scenario}_{ai_agent_role}"
                ),
            )

            st.caption(
                f"Amount: {format_inr(ai_starting_target)}"
            )

            st.caption(
                field1_help
            )

            st.caption(
                f"Amount: {format_inr(ai_reservation_price)}"
            )

            st.caption(
                field2_help
            )

            ai_instructions = st.text_area(
                "Custom Instructions",
                placeholder=(
                    "Optional instructions for the AI agent..."
                ),
                height=120,
                key=(
                    f"practice_ai_instructions_"
                    f"{scenario}_{ai_agent_role}"
                ),
            )

    # ========================================================
    # BUILD PRACTICE CONFIG
    # ========================================================

    human_config = {

        "name": (
            scenario_agents["agent1_name"]
            if role
            == scenario_agents["agent1_role"]
            else scenario_agents["agent2_name"]
        ),

        "role": role,

        "strategy": human_strategy,

        "scenario": scenario,

        "starting_target": float(
            human_starting_target
        ),

        "reservation_price": float(
            human_reservation_price
        ),

        "instructions": human_instructions,
    }

    ai_config = {

        "name": ai_agent_name,

        "role": ai_agent_role,

        "strategy": ai_strategy,

        "scenario": scenario,

        "starting_target": float(
            ai_starting_target
        ),

        "reservation_price": float(
            ai_reservation_price
        ),

        "instructions": ai_instructions,
    }

    if (
        role
        == scenario_agents["agent1_role"]
    ):

        st.session_state.agent1_config = (
            human_config
        )

        st.session_state.agent2_config = (
            ai_config
        )

    else:

        st.session_state.agent1_config = (
            ai_config
        )

        st.session_state.agent2_config = (
            human_config
        )


# ============================================================
# AI VS AI
# ============================================================

if st.session_state.mode == "Simulation":

    st.divider()

    st.subheader(
        "🤖 Configure AI Agents"
    )

    st.caption(
        "Configure both autonomous participants."
    )

    agent1_col, agent2_col = st.columns(
        2,
        gap="large",
    )

    # ========================================================
    # AGENT 1
    # ========================================================

    with agent1_col:

        with st.container(border=True):

            st.markdown(
                "### 🟣 Agent 1"
            )

            st.caption(
                "First negotiation participant"
            )

            st.divider()

            agent1_name = st.text_input(
                "Agent Name",
                value=scenario_agents[
                    "agent1_name"
                ],
                key="agent1_name",
            )

            agent1_role = st.text_input(
                "Role",
                value=scenario_agents[
                    "agent1_role"
                ],
                key="agent1_role",
            )

            agent1_strategy = st.selectbox(
                "Negotiation Strategy",
                STRATEGIES,
                key="agent1_strategy",
            )

            agent1_field1 = st.number_input(
                field1_label,
                min_value=0.0,
                value=float(
                    agent1_field1_default
                ),
                step=1000.0,
                key=f"agent1_field1_{scenario}",
            )

            st.caption(
                f"Amount: {format_inr(agent1_field1)}"
            )

            st.caption(
                field1_help
            )

            agent1_field2 = st.number_input(
                field2_label,
                min_value=0.0,
                value=float(
                    agent1_field2_default
                ),
                step=1000.0,
                key=f"agent1_field2_{scenario}",
            )

            st.caption(
                f"Amount: {format_inr(agent1_field2)}"
            )

            st.caption(
                field2_help
            )

            agent1_instructions = st.text_area(
                "Custom Instructions",
                placeholder=(
                    "Optional instructions for Agent 1..."
                ),
                height=100,
                key="agent1_instructions",
            )

    # ========================================================
    # AGENT 2
    # ========================================================

    with agent2_col:

        with st.container(border=True):

            st.markdown(
                "### 🟠 Agent 2"
            )

            st.caption(
                "Second negotiation participant"
            )

            st.divider()

            agent2_name = st.text_input(
                "Agent Name",
                value=scenario_agents[
                    "agent2_name"
                ],
                key="agent2_name",
            )

            agent2_role = st.text_input(
                "Role",
                value=scenario_agents[
                    "agent2_role"
                ],
                key="agent2_role",
            )

            agent2_strategy = st.selectbox(
                "Negotiation Strategy",
                STRATEGIES,
                index=1,
                key="agent2_strategy",
            )

            agent2_field1 = st.number_input(
                field1_label,
                min_value=0.0,
                value=float(
                    agent2_field1_default
                ),
                step=1000.0,
                key=f"agent2_field1_{scenario}",
            )

            st.caption(
                f"Amount: {format_inr(agent2_field1)}"
            )

            st.caption(
                field1_help
            )

            agent2_field2 = st.number_input(
                field2_label,
                min_value=0.0,
                value=float(
                    agent2_field2_default
                ),
                step=1000.0,
                key=f"agent2_field2_{scenario}",
            )

            st.caption(
                f"Amount: {format_inr(agent2_field2)}"
            )

            st.caption(
                field2_help
            )

            agent2_instructions = st.text_area(
                "Custom Instructions",
                placeholder=(
                    "Optional instructions for Agent 2..."
                ),
                height=100,
                key="agent2_instructions",
            )


# ============================================================
# STEP 3 — CONFIGURATION
# ============================================================

st.divider()

st.subheader(
    "⚙️ Step 3 — Configuration"
)

config_left, config_right = st.columns(
    2,
    gap="large",
)


with config_left:

    max_rounds = st.slider(
        "Maximum Rounds",
        min_value=5,
        max_value=20,
        value=st.session_state.max_rounds,
    )

    agreement = st.slider(
        "Agreement Threshold (%)",
        min_value=50,
        max_value=100,
        value=st.session_state.agreement,
    )


with config_right:

    response_time = st.slider(
        "AI Response Time",
        min_value=1,
        max_value=5,
        value=st.session_state.response_time,
    )

    logging = st.checkbox(
        "Enable Logging",
        value=st.session_state.logging,
    )


# ============================================================
# SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📄 Negotiation Summary"
)

summary1, summary2, summary3, summary4 = st.columns(
    4
)

with summary1:

    st.caption(
        "Scenario"
    )

    st.write(
        scenario
    )


with summary2:

    st.caption(
        "Mode"
    )

    st.write(
        st.session_state.mode
        if st.session_state.mode
        else "Not Selected"
    )


with summary3:

    st.caption(
        "Maximum Rounds"
    )

    st.write(
        max_rounds
    )


with summary4:

    st.caption(
        "Participants"
    )

    if st.session_state.mode == "Simulation":

        st.write(
            "AI Agents"
        )

    elif st.session_state.mode == "Practice":

        st.write(
            "Human + AI"
        )

    else:

        st.write(
            "Not Selected"
        )


# ============================================================
# AI SUMMARY
# ============================================================

if st.session_state.mode == "Simulation":

    st.divider()

    st.subheader(
        "🤖 Agent Configuration Summary"
    )

    summary_agent1, summary_agent2 = st.columns(
        2,
        gap="large",
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
                f"**{field1_label}:** "
                f"{format_inr(agent1_field1)}"
            )

            st.write(
                f"**{field2_label}:** "
                f"{format_inr(agent1_field2)}"
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
                f"**{field1_label}:** "
                f"{format_inr(agent2_field1)}"
            )

            st.write(
                f"**{field2_label}:** "
                f"{format_inr(agent2_field2)}"
            )


# ============================================================
# START NEGOTIATION
# ============================================================

st.divider()

if st.button(
    "🚀 Start Negotiation",
    width="stretch",
    type="primary",
):

    # ========================================================
    # VALIDATION
    # ========================================================

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
    # BUILD / VALIDATE AI CONFIGURATION
    # ========================================================

    if st.session_state.mode == "Simulation":

        if (
            agent1_field1 <= 0
            or agent1_field2 <= 0
        ):

            st.error(
                "Agent 1 values must be greater than 0."
            )

            st.stop()


        if (
            agent2_field1 <= 0
            or agent2_field2 <= 0
        ):

            st.error(
                "Agent 2 values must be greater than 0."
            )

            st.stop()


        # ----------------------------------------------------
        # VENDOR
        # ----------------------------------------------------

        if scenario == "Vendor Pricing Negotiation":

            if agent1_field1 >= agent1_field2:

                st.error(
                    "Agent 1: Starting Target must be "
                    "less than the Reservation Price."
                )

                st.stop()


            if agent2_field1 <= agent2_field2:

                st.error(
                    "Agent 2: Starting Target must be "
                    "greater than the Reservation Price."
                )

                st.stop()


        # ----------------------------------------------------
        # JOB OFFER
        # ----------------------------------------------------

        elif scenario == "Job Offer Negotiation":

            if agent1_field1 < agent1_field2:

                st.error(
                    "Agent 1: Starting Salary must be "
                    "greater than or equal to Minimum Salary."
                )

                st.stop()


            if agent2_field1 > agent2_field2:

                st.error(
                    "Agent 2: Starting Salary must be "
                    "less than or equal to Maximum Salary."
                )

                st.stop()


        # ----------------------------------------------------
        # PROJECT BUDGET
        # ----------------------------------------------------

        elif scenario == "Project Budget Allocation":

            # Requester starts high and moves downward.

            if agent1_field1 < agent1_field2:

                st.error(
                    "Budget Requester: Starting Budget Position "
                    "must be greater than or equal to the "
                    "Walk-Away Budget."
                )

                st.stop()


            # Allocator starts low and moves upward.

            if agent2_field1 > agent2_field2:

                st.error(
                    "Budget Allocator: Starting Budget Position "
                    "must be less than or equal to the "
                    "Walk-Away Budget."
                )

                st.stop()


            # ------------------------------------------------
            # TOTAL PROJECT BUDGET
            # ------------------------------------------------

            if project_budget is not None:

                if agent1_field1 > project_budget:

                    st.error(
                        "Budget Requester: Starting Budget Position "
                        "cannot exceed the Total Project Budget."
                    )

                    st.stop()


                if agent2_field1 > project_budget:

                    st.error(
                        "Budget Allocator: Starting Budget Position "
                        "cannot exceed the Total Project Budget."
                    )

                    st.stop()


                if agent1_field2 > project_budget:

                    st.error(
                        "Budget Requester: Walk-Away Budget cannot "
                        "exceed the Total Project Budget."
                    )

                    st.stop()


                if agent2_field2 > project_budget:

                    st.error(
                        "Budget Allocator: Walk-Away Budget cannot "
                        "exceed the Total Project Budget."
                    )

                    st.stop()


        # ====================================================
        # STORE AGENT 1 CONFIG
        # ====================================================

        st.session_state.agent1_config = {

            "name": agent1_name,

            "role": agent1_role,

            "strategy": agent1_strategy,

            "scenario": scenario,

            "starting_target": float(
                agent1_field1
            ),

            "reservation_price": float(
                agent1_field2
            ),

            "instructions": agent1_instructions,
        }


        # ====================================================
        # STORE AGENT 2 CONFIG
        # ====================================================

        st.session_state.agent2_config = {

            "name": agent2_name,

            "role": agent2_role,

            "strategy": agent2_strategy,

            "scenario": scenario,

            "starting_target": float(
                agent2_field1
            ),

            "reservation_price": float(
                agent2_field2
            ),

            "instructions": agent2_instructions,
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
    # PAYLOAD
    # ========================================================

    payload = {

        "scenario": scenario,

        "mode": backend_mode,

        "max_rounds": max_rounds,

        "agreement_threshold": agreement,

        "response_time": response_time,

        "logging": logging,
    }


    # ========================================================
    # PROJECT BUDGET
    # ========================================================

    if (
        scenario == "Project Budget Allocation"
        and project_budget is not None
    ):

        # IMPORTANT:
        # This name must match NegotiationRequest.
        payload["project_total_budget"] = float(
            project_budget
        )


    # ========================================================
    # AI VS AI
    # ========================================================

    if st.session_state.mode == "Simulation":

        # IMPORTANT:
        # These names must exactly match:
        #
        # NegotiationRequest.agent1_config
        # NegotiationRequest.agent2_config
        #
        payload["agent1_config"] = (
            st.session_state.agent1_config
        )

        payload["agent2_config"] = (
            st.session_state.agent2_config
        )


    # ========================================================
    # HUMAN VS AI
    # ========================================================

    elif st.session_state.mode == "Practice":

        payload["role"] = (
            st.session_state.role
        )

        # Keep the already-built configurations available
        # for future practice-mode persistence.
        payload["agent1_config"] = (
            st.session_state.agent1_config
        )

        payload["agent2_config"] = (
            st.session_state.agent2_config
        )


    # ========================================================
    # START BACKEND
    # ========================================================

    try:

        with st.spinner(
            "Starting negotiation..."
        ):

            response = requests.post(
                "http://127.0.0.1:8000/start-negotiation",
                json=payload,
                timeout=15,
            )


        if response.status_code != 200:

            st.error(
                f"Backend Error: {response.text}"
            )

            st.stop()


        data = response.json()


        # ====================================================
        # SAVE SESSION
        # ====================================================

        st.session_state.session_id = data.get(
            "session_id",
            "",
        )

        st.session_state.scenario = scenario

        st.session_state.max_rounds = max_rounds

        st.session_state.agreement = agreement

        st.session_state.response_time = response_time

        st.session_state.logging = logging


        # ====================================================
        # RESET SIMULATION STATE
        # ====================================================

        if backend_mode == "AI vs AI":

            st.session_state.simulation_messages = []

            st.session_state.simulation_round = 0

            st.session_state.simulation_status = (
                "Waiting"
            )

            st.session_state.simulation_finished = False

            st.session_state.active_agent = None

            st.session_state.waiting_for_response = False


            st.switch_page(
                "pages/Simulation.py"
            )


        # ====================================================
        # PRACTICE
        # ====================================================

        else:

            st.session_state.messages = []

            st.switch_page(
                "pages/Live_Negotiation.py"
            )


    except requests.exceptions.RequestException as e:

        st.error(
            "Unable to connect to backend.\n\n"
            f"{e}"
        )