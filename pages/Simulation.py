import streamlit as st
import requests
import time
import re

from components.styles import load_css
from components.navbar import show_navbar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI vs AI Simulation",
    page_icon="🤖",
    layout="wide",
)

load_css()
show_navbar()


# ============================================================
# BACKEND
# ============================================================

BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

defaults = {
    "simulation_messages": [],
    "simulation_started": False,
    "simulation_finished": False,
    "simulation_round": 0,
    "simulation_status": "Waiting",
    "active_agent": None,
    "waiting_for_response": False,
    "backend_agent1": None,
    "backend_agent2": None,
    "response_time": 2,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SESSION
# ============================================================

session_id = st.session_state.get(
    "session_id",
    "",
)

if not session_id:

    st.error(
        "No active negotiation found."
    )

    st.stop()


scenario = st.session_state.get(
    "scenario",
    "Vendor Pricing Negotiation",
)

max_rounds = st.session_state.get(
    "max_rounds",
    10,
)


# ============================================================
# SCENARIO AGENTS
# ============================================================

SCENARIO_AGENTS = {

    "Vendor Pricing Negotiation": {
        "agent1": "Buyer",
        "agent2": "Supplier",
    },

    "Job Offer Negotiation": {
        "agent1": "Candidate",
        "agent2": "HR Manager",
    },

    "Project Budget Allocation": {
        "agent1": "Budget Requester",
        "agent2": "Budget Allocator",
    },
}


fallback_agents = SCENARIO_AGENTS.get(
    scenario,
    {
        "agent1": "Agent 1",
        "agent2": "Agent 2",
    },
)


# ============================================================
# BACKEND GET
# ============================================================

def get_negotiation_state():

    try:

        response = requests.get(
            f"{BASE_URL}/negotiation/{session_id}",
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("error"):
            return None

        return data

    except requests.exceptions.RequestException:

        return None


# ============================================================
# NORMALIZE SPEAKER
# ============================================================

def normalize_speaker(speaker):

    if speaker == "Department Representative":
        return "Budget Requester"

    if speaker == "department representative":
        return "Budget Requester"

    return speaker


# ============================================================
# NORMALIZE MESSAGES
# ============================================================

def normalize_messages(messages):

    normalized = []

    for message in messages or []:

        if not isinstance(message, dict):
            continue

        item = dict(message)

        item["speaker"] = normalize_speaker(
            item.get("speaker")
        )

        normalized.append(item)

    return normalized


# ============================================================
# APPLY BACKEND STATUS
# ============================================================

def apply_backend_status(status):

    if status == "agreement_reached":

        st.session_state.simulation_status = (
            "Agreement Reached"
        )

        st.session_state.simulation_finished = True
        st.session_state.active_agent = None


    elif status == "deadlock":

        st.session_state.simulation_status = (
            "Deadlock"
        )

        st.session_state.simulation_finished = True
        st.session_state.active_agent = None


    elif status == "quota_exceeded":

        st.session_state.simulation_status = (
            "Quota Exceeded"
        )

        st.session_state.simulation_finished = True
        st.session_state.active_agent = None


    elif status == "max_rounds_reached":

        st.session_state.simulation_status = (
            "Maximum Rounds Reached"
        )

        st.session_state.simulation_finished = True
        st.session_state.active_agent = None


    elif status == "completed":

        st.session_state.simulation_status = (
            "Maximum Rounds Reached"
        )

        st.session_state.simulation_finished = True
        st.session_state.active_agent = None


    else:

        st.session_state.simulation_status = (
            "Negotiating"
        )


# ============================================================
# REFRESH STATE
# ============================================================

def refresh_state():

    data = get_negotiation_state()

    if not data:
        return False

    # --------------------------------------------------------
    # AGENTS
    # --------------------------------------------------------

    backend_agent1 = data.get(
        "agent1"
    )

    backend_agent2 = data.get(
        "agent2"
    )

    if backend_agent1:

        st.session_state.backend_agent1 = (
            normalize_speaker(
                backend_agent1
            )
        )

    if backend_agent2:

        st.session_state.backend_agent2 = (
            normalize_speaker(
                backend_agent2
            )
        )


    # --------------------------------------------------------
    # MESSAGES
    # --------------------------------------------------------

    st.session_state.simulation_messages = (
        normalize_messages(
            data.get(
                "messages",
                [],
            )
        )
    )


    # --------------------------------------------------------
    # ROUND
    # --------------------------------------------------------

    st.session_state.simulation_round = (
        data.get(
            "round",
            0,
        )
    )


    # --------------------------------------------------------
    # MAX ROUNDS
    # --------------------------------------------------------

    backend_max_rounds = data.get(
        "max_rounds"
    )

    if backend_max_rounds is not None:

        st.session_state.max_rounds = (
            backend_max_rounds
        )


    # --------------------------------------------------------
    # ACTIVE AGENT
    # --------------------------------------------------------

    if not st.session_state.simulation_finished:

        st.session_state.active_agent = (
            normalize_speaker(
                data.get(
                    "active_agent"
                )
            )
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    apply_backend_status(
        data.get(
            "status",
            "in_progress",
        )
    )

    return True


# ============================================================
# AUTHORITATIVE AGENT NAMES
# ============================================================

agent1_name = (
    st.session_state.backend_agent1
    or fallback_agents["agent1"]
)

agent2_name = (
    st.session_state.backend_agent2
    or fallback_agents["agent2"]
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 AI vs AI Negotiation"
)

st.write(
    f"### {scenario}"
)

st.caption(
    "Two autonomous AI agents are negotiating automatically."
)

st.divider()


# ============================================================
# INITIALIZE
# ============================================================

if not st.session_state.simulation_started:

    st.session_state.simulation_started = True

    st.session_state.simulation_status = (
        "Negotiating"
    )

    refresh_state()


# ============================================================
# REFRESH BACKEND STATE
# ============================================================

if not st.session_state.simulation_finished:

    refresh_state()


# ============================================================
# DETERMINE IF NEGOTIATION SHOULD CONTINUE
# ============================================================

should_continue = (
    not st.session_state.simulation_finished
    and not st.session_state.waiting_for_response
)


# ============================================================
# EXECUTE ONE TURN
# ============================================================

if should_continue:

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # The backend controls the speaker.
    #
    # We only ask it for ONE turn.
    # --------------------------------------------------------

    st.session_state.waiting_for_response = True

    st.session_state.simulation_status = (
        "Thinking"
    )

    response_time = st.session_state.get(
        "response_time",
        2,
    )

    # --------------------------------------------------------
    # THINKING DELAY
    # --------------------------------------------------------

    time.sleep(
        response_time
    )

    try:

        response = requests.post(
            f"{BASE_URL}/simulate-next-turn",
            json={
                "session_id": session_id
            },
            timeout=120,
        )


        # ====================================================
        # BACKEND ERROR
        # ====================================================

        if response.status_code != 200:

            st.session_state.waiting_for_response = False

            st.session_state.simulation_status = (
                "Backend Error"
            )

            st.session_state.simulation_finished = True

            st.session_state.active_agent = None

            st.error(
                f"Backend error: {response.text}"
            )


        else:

            result = response.json()

            # ------------------------------------------------
            # REFRESH AFTER TURN
            # ------------------------------------------------

            refresh_state()

            # ------------------------------------------------
            # APPLY EXACT BACKEND STATUS
            # ------------------------------------------------

            apply_backend_status(
                result.get(
                    "status",
                    "in_progress",
                )
            )

            # ------------------------------------------------
            # TURN COMPLETE
            # ------------------------------------------------

            st.session_state.waiting_for_response = False


    except requests.exceptions.RequestException as e:

        st.session_state.waiting_for_response = False

        st.session_state.simulation_status = (
            "Backend Error"
        )

        st.session_state.simulation_finished = True

        st.session_state.active_agent = None

        st.error(
            "Unable to connect to backend.\n\n"
            f"{e}"
        )


# ============================================================
# FINAL STATE REFRESH
# ============================================================

if not st.session_state.simulation_finished:

    refresh_state()


# ============================================================
# STATUS
# ============================================================

status = st.session_state.simulation_status


if status == "Agreement Reached":

    st.success(
        "✅ Agreement Reached"
    )


elif status == "Deadlock":

    st.warning(
        "⚠️ Negotiation ended due to deadlock."
    )


elif status == "Quota Exceeded":

    st.error(
        "⛔ Gemini API quota exceeded."
    )


elif status == "Maximum Rounds Reached":

    st.warning(
        "⚠️ Maximum negotiation rounds reached."
    )


elif status == "Thinking":

    st.info(
        "🤖 AI is thinking..."
    )


elif status == "Backend Error":

    st.error(
        "❌ Backend connection error."
    )


else:

    st.info(
        "🤖 AI agents are negotiating automatically..."
    )


# ============================================================
# AGENT CARDS
# ============================================================

agent1_col, agent2_col = st.columns(
    2,
    gap="large",
)


# ============================================================
# AGENT CARD FUNCTION
# ============================================================

def render_agent_card(
    agent_name,
    icon,
):

    with st.container(border=True):

        st.markdown(
            f"## {icon} {agent_name}"
        )

        st.caption(
            f"Role: {agent_name}"
        )

        st.divider()

        # ----------------------------------------------------
        # ACTIVE
        # ----------------------------------------------------

        if (
            st.session_state.active_agent
            == agent_name
            and not st.session_state.simulation_finished
        ):

            st.warning(
                "🟡 AI is thinking..."
            )


        # ----------------------------------------------------
        # FINISHED
        # ----------------------------------------------------

        elif st.session_state.simulation_finished:

            st.success(
                "🟢 Negotiation Complete"
            )


        # ----------------------------------------------------
        # WAITING
        # ----------------------------------------------------

        else:

            st.success(
                "🟢 Waiting for turn"
            )


        # ----------------------------------------------------
        # MESSAGES
        # ----------------------------------------------------

        agent_messages = [

            message

            for message
            in st.session_state.simulation_messages

            if normalize_speaker(
                message.get("speaker")
            )
            == agent_name

        ]


        # ----------------------------------------------------
        # LATEST MESSAGE
        # ----------------------------------------------------

        if agent_messages:

            latest = agent_messages[-1]

            st.markdown(
                "**Latest Response**"
            )

            st.write(
                latest.get(
                    "message",
                    "",
                )
            )

        else:

            st.caption(
                "Waiting for negotiation..."
            )


# ============================================================
# AGENT 1
# ============================================================

with agent1_col:

    render_agent_card(
        agent1_name,
        "🟣",
    )


# ============================================================
# AGENT 2
# ============================================================

with agent2_col:

    render_agent_card(
        agent2_name,
        "🟠",
    )


# ============================================================
# ACTIVE AGENT
# ============================================================

st.divider()


if (
    st.session_state.active_agent
    and not st.session_state.simulation_finished
):

    st.info(
        f"🤖 **{st.session_state.active_agent}** "
        "is currently negotiating..."
    )


elif st.session_state.simulation_finished:

    st.success(
        "✅ Both agents have completed the negotiation."
    )


# ============================================================
# NEGOTIATION INFORMATION
# ============================================================

st.divider()

info1, info2, info3 = st.columns(
    3
)


with info1:

    st.metric(
        "Negotiation Round",
        (
            f"{st.session_state.simulation_round}"
            f"/{st.session_state.max_rounds}"
        ),
    )


with info2:

    st.metric(
        "Mode",
        "AI vs AI",
    )


with info3:

    st.metric(
        "Status",
        status,
    )


# ============================================================
# FINAL RESULT
# ============================================================

if st.session_state.simulation_finished:

    st.divider()

    st.subheader(
        "🎉 Negotiation Result"
    )


    # ========================================================
    # AGREEMENT
    # ========================================================

    if status == "Agreement Reached":

        st.success(
            "✅ Agreement Reached Successfully"
        )

        result_col1, result_col2 = st.columns(
            2
        )


        with result_col1:

            st.markdown(
                "### 🤝 Final Agreement"
            )

            final_message = ""

            for message in reversed(
                st.session_state.simulation_messages
            ):

                speaker = normalize_speaker(
                    message.get(
                        "speaker",
                        "",
                    )
                )

                if speaker in (
                    agent1_name,
                    agent2_name,
                ):

                    final_message = message.get(
                        "message",
                        "",
                    )

                    break


            st.info(
                final_message
                if final_message
                else
                "Agreement successfully reached."
            )


        with result_col2:

            st.markdown(
                "### 📊 Negotiation Summary"
            )

            st.metric(
                "Rounds Completed",
                (
                    f"{st.session_state.simulation_round}"
                    f"/{st.session_state.max_rounds}"
                ),
            )

            st.metric(
                "Mode",
                "AI vs AI",
            )

            st.metric(
                "Participants",
                f"{agent1_name} ↔ {agent2_name}",
            )


    # ========================================================
    # DEADLOCK
    # ========================================================

    elif status == "Deadlock":

        st.warning(
            "⚠️ Negotiation ended without an agreement."
        )


    # ========================================================
    # MAX ROUNDS
    # ========================================================

    elif status == "Maximum Rounds Reached":

        st.warning(
            "⚠️ Maximum negotiation rounds reached."
        )


    # ========================================================
    # QUOTA
    # ========================================================

    elif status == "Quota Exceeded":

        st.error(
            "⛔ Negotiation stopped because "
            "the Gemini API quota was exceeded."
        )


# ============================================================
# ANALYTICS
# ============================================================

if st.session_state.simulation_finished:

    st.divider()

    st.subheader(
        "📊 Negotiation Analytics"
    )

    messages = (
        st.session_state.simulation_messages
    )


    # ========================================================
    # NEGOTIATION MESSAGES
    # ========================================================

    negotiation_messages = [

        message

        for message in messages

        if normalize_speaker(
            message.get("speaker")
        )
        in (
            agent1_name,
            agent2_name,
        )

    ]


    # ========================================================
    # MONEY EXTRACTION
    # ========================================================

    def extract_money_values(text):

        values = []

        if not text:
            return values

        pattern = re.compile(
            r"₹\s*([\d,]+(?:\.\d+)?)\s*"
            r"(LPA|lakhs?|lakh)?",
            flags=re.IGNORECASE,
        )

        for match in pattern.finditer(text):

            raw_value = (
                match.group(1)
                .replace(",", "")
            )

            unit = (
                match.group(2)
                or ""
            ).lower()

            try:

                value = float(
                    raw_value
                )

            except ValueError:

                continue


            if unit == "lpa":

                value *= 100000


            elif unit in (
                "lakh",
                "lakhs",
            ):

                value *= 100000


            values.append(
                value
            )

        return values


    # ========================================================
    # FORMAT LPA
    # ========================================================

    def format_lpa(value):

        lpa = (
            float(value)
            / 100000
        )

        if lpa.is_integer():

            return (
                f"₹{int(lpa)} LPA"
            )

        return (
            f"₹{lpa:.1f} LPA"
        )


    # ========================================================
    # EXTRACT VALUES
    # ========================================================

    extracted_values = []

    for message in negotiation_messages:

        text = message.get(
            "message",
            "",
        )

        extracted_values.extend(
            extract_money_values(
                text
            )
        )


    # ========================================================
    # PROJECT BUDGET FILTER
    # ========================================================

    if scenario == "Project Budget Allocation":

        filtered_values = []

        for message in negotiation_messages:

            speaker = normalize_speaker(
                message.get(
                    "speaker",
                    "",
                )
            )

            text = message.get(
                "message",
                "",
            )

            lower_text = text.lower()


            # ------------------------------------------------
            # Ignore total project budget references.
            # ------------------------------------------------

            if (
                "total project budget"
                in lower_text
                or
                "total budget available"
                in lower_text
            ):

                continue


            filtered_values.extend(
                extract_money_values(
                    text
                )
            )


        extracted_values = filtered_values


    # ========================================================
    # VENDOR ANALYTICS
    # ========================================================

    if (
        scenario
        == "Vendor Pricing Negotiation"
        and extracted_values
    ):

        starting_price = (
            extracted_values[0]
        )

        final_price = (
            extracted_values[-1]
        )

        price_difference = (
            starting_price
            - final_price
        )


        st.markdown(
            "### 💰 Pricing Analysis"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            st.metric(
                "Starting Price",
                f"₹{starting_price:,.0f}",
            )


        with col2:

            st.metric(
                "Final Price",
                f"₹{final_price:,.0f}",
            )


        with col3:

            st.metric(
                "Price Difference",
                f"₹{price_difference:,.0f}",
            )


    # ========================================================
    # JOB OFFER ANALYTICS
    # ========================================================

    elif (
        scenario
        == "Job Offer Negotiation"
        and extracted_values
    ):

        starting_salary = (
            extracted_values[0]
        )

        final_salary = (
            extracted_values[-1]
        )

        salary_difference = (
            final_salary
            - starting_salary
        )


        st.markdown(
            "### 💼 Salary Analysis"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            st.metric(
                "Initial Salary",
                format_lpa(
                    starting_salary
                ),
            )


        with col2:

            st.metric(
                "Final Salary",
                format_lpa(
                    final_salary
                ),
            )


        with col3:

            st.metric(
                "Salary Increase",
                format_lpa(
                    salary_difference
                ),
            )


    # ========================================================
    # PROJECT BUDGET ANALYTICS
    # ========================================================

    elif (
        scenario
        == "Project Budget Allocation"
        and extracted_values
    ):

        initial_budget = (
            extracted_values[0]
        )

        final_budget = (
            extracted_values[-1]
        )

        budget_difference = (
            initial_budget
            - final_budget
        )


        st.markdown(
            "### 💰 Budget Analysis"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            st.metric(
                "Initial Request",
                f"₹{initial_budget:,.0f}",
            )


        with col2:

            st.metric(
                "Final Allocation",
                f"₹{final_budget:,.0f}",
            )


        with col3:

            st.metric(
                "Difference",
                f"₹{budget_difference:,.0f}",
            )


    # ========================================================
    # GENERAL STATS
    # ========================================================

    st.markdown(
        "### 📈 Negotiation Statistics"
    )


    stat1, stat2, stat3 = st.columns(
        3
    )


    with stat1:

        st.metric(
            "Rounds Completed",
            (
                f"{st.session_state.simulation_round}"
                f"/{st.session_state.max_rounds}"
            ),
        )


    with stat2:

        st.metric(
            "AI Turns",
            len(
                negotiation_messages
            ),
        )


    with stat3:

        st.metric(
            "Outcome",
            status,
        )


# ============================================================
# ZIG-ZAG CONVERSATION
# ============================================================

st.divider()

st.subheader(
    "💬 Negotiation Conversation"
)


if not st.session_state.simulation_messages:

    st.info(
        "Waiting for the AI agents to start negotiating..."
    )


else:

    for index, message in enumerate(
        st.session_state.simulation_messages
    ):

        speaker = normalize_speaker(
            message.get(
                "speaker",
                "AI Agent",
            )
        )

        text = message.get(
            "message",
            "",
        )

        # ----------------------------------------------------
        # ROUND
        # ----------------------------------------------------

        negotiation_index = 0

        for previous_message in (
            st.session_state.simulation_messages[
                :index
            ]
        ):

            previous_speaker = normalize_speaker(
                previous_message.get(
                    "speaker",
                    "",
                )
            )

            if previous_speaker in (
                agent1_name,
                agent2_name,
            ):

                negotiation_index += 1


        if speaker in (
            agent1_name,
            agent2_name,
        ):

            round_number = (
                (negotiation_index + 1)
                // 2
            )

            if round_number <= 0:
                round_text = "Opening"
            else:
                round_text = (
                    f"Round {round_number}"
                )

        else:

            round_text = ""


        # ====================================================
        # SYSTEM
        # ====================================================

        if speaker == "System":

            st.success(
                f"🤝 **System**"
                f"{' • ' + round_text if round_text else ''}"
                f"\n\n{text}"
            )

            continue


        # ====================================================
        # AGENT 1
        # ====================================================

        is_agent1 = (
            speaker == agent1_name
        )


        # ====================================================
        # AGENT 2
        # ====================================================

        is_agent2 = (
            speaker == agent2_name
        )


        # ====================================================
        # UNKNOWN
        # ====================================================

        if not is_agent1 and not is_agent2:

            st.warning(
                f"⚠️ Unknown speaker: {speaker}"
            )

            st.write(
                text
            )

            continue


        # ====================================================
        # ZIG-ZAG ROW
        # ====================================================

        left_col, right_col = st.columns(
            [1, 1],
            gap="large",
        )


        # ====================================================
        # AGENT 1 → LEFT
        # ====================================================

        if is_agent1:

            with left_col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🟣 {speaker}"
                    )

                    st.caption(
                        round_text
                    )

                    st.write(
                        text
                    )


            with right_col:

                st.empty()


        # ====================================================
        # AGENT 2 → RIGHT
        # ====================================================

        elif is_agent2:

            with left_col:

                st.empty()


            with right_col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🟠 {speaker}"
                    )

                    st.caption(
                        round_text
                    )

                    st.write(
                        text
                    )


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

if not st.session_state.simulation_finished:

    time.sleep(1)

    st.rerun()


# ============================================================
# BOTTOM ACTIONS
# ============================================================

st.divider()

back_col, restart_col = st.columns(
    2
)


# ============================================================
# HOME
# ============================================================

with back_col:

    if st.button(
        "🏠 Back to Home",
        use_container_width=True,
    ):

        st.session_state.simulation_finished = True

        st.switch_page(
            "pages/Home.py"
        )


# ============================================================
# RESTART
# ============================================================

with restart_col:

    if st.button(
        "🔄 Restart Simulation",
        use_container_width=True,
    ):

        st.session_state.simulation_messages = []

        st.session_state.simulation_started = False

        st.session_state.simulation_finished = False

        st.session_state.simulation_round = 0

        st.session_state.simulation_status = (
            "Waiting"
        )

        st.session_state.active_agent = None

        st.session_state.waiting_for_response = False

        st.session_state.backend_agent1 = None

        st.session_state.backend_agent2 = None

        st.rerun()