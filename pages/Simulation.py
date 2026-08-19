import streamlit as st
import requests
import time

from components.styles import load_css
from components.navbar import show_navbar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI vs AI Simulation",
    page_icon="🤖",
    layout="wide"
)

load_css()
show_navbar()


# ============================================================
# SESSION STATE
# ============================================================

scenario = st.session_state.get("scenario", "")
mode = st.session_state.get("mode", "AI vs AI")
max_rounds = st.session_state.get("max_rounds", 10)
session_id = st.session_state.get("session_id", "")

if not session_id:
    st.error("No active negotiation found.")
    st.stop()


defaults = {
    "simulation_messages": [],
    "simulation_started": False,
    "simulation_finished": False,
    "simulation_round": 0,
    "simulation_status": "Waiting",
    "active_agent": None,
    "waiting_for_response": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GET NEGOTIATION DETAILS
# ============================================================

scenario = st.session_state.get(
    "scenario",
    "Vendor Pricing Negotiation"
)

session_id = st.session_state.get(
    "session_id",
    ""
)

max_rounds = st.session_state.get(
    "max_rounds",
    10
)

agent1 = st.session_state.get(
    "agent1_config",
    {}
)

agent2 = st.session_state.get(
    "agent2_config",
    {}
)

agent1_name = agent1.get(
    "name",
    "Buyer"
)

agent1_role = agent1.get(
    "role",
    "Buyer"
)

agent2_name = agent2.get(
    "name",
    "Supplier"
)

agent2_role = agent2.get(
    "role",
    "Supplier"
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI vs AI Negotiation")

st.write(
    f"### {scenario}"
)

st.caption(
    "Two autonomous AI agents are negotiating automatically."
)

st.divider()

# ============================================================
# AUTOMATIC BACKEND NEGOTIATION — ONE TURN AT A TIME
# ============================================================

if (
    session_id
    and not st.session_state.simulation_started
):

    st.session_state.simulation_started = True
    st.session_state.simulation_status = "Negotiating"

    # The opening message already exists from /start-negotiation.
    # Get the latest negotiation state first.

    try:

        response = requests.get(
            f"http://127.0.0.1:8000/negotiation/{session_id}",
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            messages = data.get(
                "messages",
                []
            )

            st.session_state.simulation_messages = messages

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to backend.\n\n{e}"
        )

        st.session_state.simulation_finished = True


# ============================================================
# EXECUTE ONE AI TURN
# ============================================================

if (
    session_id
    and st.session_state.simulation_started
    and not st.session_state.simulation_finished
):

    try:

        # Determine which agent should respond
        conversation = st.session_state.simulation_messages

        negotiation_speakers = [
            msg.get("speaker")
            for msg in conversation
            if msg.get("speaker") in [
                agent1_name,
                agent1_role,
                agent2_name,
                agent2_role
            ]
        ]

        if negotiation_speakers:

            last_speaker = negotiation_speakers[-1]

            if last_speaker in (
                agent1_name,
                agent1_role
            ):

                st.session_state.active_agent = agent2_name

            else:

                st.session_state.active_agent = agent1_name

        else:

            st.session_state.active_agent = agent1_name

        # ----------------------------------------------------
        # AI THINKING STATE
        # ----------------------------------------------------

        if not st.session_state.waiting_for_response:

            st.session_state.simulation_status = "Thinking"
            st.session_state.waiting_for_response = True

            st.rerun()

        # ----------------------------------------------------
        # ASK BACKEND FOR ONE AI TURN
        # ----------------------------------------------------
        time.sleep(
            st.session_state.get(
                "response_time",
                2
            )
        )

        response = requests.post(
            "http://127.0.0.1:8000/simulate-next-turn",
            json={
                "session_id": session_id
            },
            timeout=120
        )

        if response.status_code == 200:

            st.session_state.waiting_for_response = False

            data = response.json()

            status = data.get(
                "status",
                "in_progress"
            )

            # Update completed round from simulation response
            if "round" in data:
                st.session_state.simulation_round = data["round"]

            # Refresh conversation
            conversation_response = requests.get(
                f"http://127.0.0.1:8000/negotiation/{session_id}",
                timeout=10
            )

            if conversation_response.status_code == 200:

                negotiation_data = (
                    conversation_response.json()
                )

                messages = negotiation_data.get(
                    "messages",
                    []
                )

                st.session_state.simulation_messages = (
                    messages
                )

                st.session_state.simulation_round = (
                    negotiation_data.get(
                        "round",
                        st.session_state.simulation_round
                    )
                )

            # ------------------------------------------------
            # FINISHED STATES
            # ------------------------------------------------

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

            else:

                st.session_state.simulation_status = (
                    "Negotiating"
                )

        else:

            st.session_state.waiting_for_response = False

            st.error(
                f"Backend error: {response.text}"
            )

            st.session_state.simulation_finished = True
            st.session_state.active_agent = None

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to backend.\n\n{e}"
        )
        st.session_state.waiting_for_response = False
        st.session_state.simulation_finished = True
        st.session_state.active_agent = None

# ============================================================
# GET LATEST NEGOTIATION STATE
# ============================================================

if session_id:

    try:

        response = requests.get(
            f"http://127.0.0.1:8000/negotiation/{session_id}",
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            # ------------------------------------------------
            # ACTIVE AGENT
            # ------------------------------------------------

            active_agent = data.get(
                "active_agent",
                None
            )

            if not st.session_state.simulation_finished:
                st.session_state.active_agent = active_agent


            # ------------------------------------------------
            # ROUND
            # ------------------------------------------------

            backend_round = data.get(
                "round",
                st.session_state.simulation_round
            )

            st.session_state.simulation_round = backend_round


            # ------------------------------------------------
            # MESSAGES
            # ------------------------------------------------

            messages = data.get(
                "messages",
                []
            )

            if messages:
                st.session_state.simulation_messages = messages


            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            backend_status = data.get(
                "status",
                "in_progress"
            )

            if backend_status == "agreement_reached":

                st.session_state.simulation_status = (
                    "Agreement Reached"
                )

                st.session_state.simulation_finished = True
                st.session_state.active_agent = None

            elif backend_status == "deadlock":

                st.session_state.simulation_status = (
                    "Deadlock"
                )

                st.session_state.simulation_finished = True
                st.session_state.active_agent = None

            elif backend_status == "quota_exceeded":

                st.session_state.simulation_status = (
                    "Quota Exceeded"
                )

                st.session_state.simulation_finished = True
                st.session_state.active_agent = None

            elif backend_status in (
                "completed",
                "max_rounds_reached"
            ):

                st.session_state.simulation_status = (
                    "Maximum Rounds Reached"
                )

                st.session_state.simulation_finished = True
                st.session_state.active_agent = None

            elif not st.session_state.simulation_finished:

                st.session_state.simulation_status = (
                    "Negotiating"
                )

    except requests.exceptions.RequestException:
        pass


# ============================================================
# NEGOTIATION STATUS
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

else:

    st.info(
        "🤖 AI agents are negotiating automatically..."
    )


# ============================================================
# AGENT CARDS
# ============================================================

agent1_col, agent2_col = st.columns(
    2,
    gap="large"
)


# ============================================================
# AGENT 1 CARD
# ============================================================

with agent1_col:

    with st.container(border=True):

        st.markdown(
            f"## 🤖 {agent1_name}"
        )

        st.caption(
            f"Role: {agent1_role}"
        )

        st.divider()

        if st.session_state.active_agent in (
            agent1_name,
            agent1_role
        ):

            st.warning(
                "🟡 AI is thinking..."
            )

        elif st.session_state.simulation_finished:

            st.success(
                "🟢 Negotiation Complete"
            )

        else:

            st.success(
                "🟢 Ready"
            )

        # Latest message from Agent 1

        agent1_messages = [
            message
            for message in st.session_state.simulation_messages
            if message.get("speaker") == agent1_name
            or message.get("speaker") == agent1_role
        ]

        if agent1_messages:

            latest = agent1_messages[-1]

            st.markdown(
                "**Latest Response**"
            )

            st.write(
                latest.get(
                    "message",
                    ""
                )
            )

        else:

            st.caption(
                "Waiting for negotiation..."
            )


# ============================================================
# AGENT 2 CARD
# ============================================================

with agent2_col:

    with st.container(border=True):

        st.markdown(
            f"## 🤖 {agent2_name}"
        )

        st.caption(
            f"Role: {agent2_role}"
        )

        st.divider()

        if st.session_state.active_agent in (
            agent2_name,
            agent2_role
        ):

            st.warning(
                "🟡 AI is thinking..."
            )

        elif st.session_state.simulation_finished:

            st.success(
                "🟢 Negotiation Complete"
            )

        else:

            st.success(
                "🟢 Ready"
            )

        # Latest message from Agent 2

        agent2_messages = [
            message
            for message in st.session_state.simulation_messages
            if message.get("speaker") == agent2_name
            or message.get("speaker") == agent2_role
        ]

        if agent2_messages:

            latest = agent2_messages[-1]

            st.markdown(
                "**Latest Response**"
            )

            st.write(
                latest.get(
                    "message",
                    ""
                )
            )

        else:

            st.caption(
                "Waiting for negotiation..."
            )
# ============================================================
# CURRENT ACTIVE AGENT
# ============================================================

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

info1, info2, info3 = st.columns(3)

with info1:

    st.metric(
        "Negotiation Round",
        f"{st.session_state.simulation_round}/{max_rounds}"
    )

with info2:

    st.metric(
        "Mode",
        "AI vs AI"
    )

with info3:

    st.metric(
        "Status",
        status
    )
# ============================================================
# FINAL NEGOTIATION RESULT
# ============================================================

if st.session_state.simulation_finished:

    st.divider()

    st.subheader("🎉 Negotiation Result")

    if status == "Agreement Reached":

        st.success(
            "✅ Agreement Reached Successfully"
        )

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.markdown("### 🤝 Final Agreement")

            # Find the latest meaningful AI message
            final_message = ""

            for message in reversed(
                st.session_state.simulation_messages
            ):

                speaker = message.get(
                    "speaker",
                    ""
                )

                if speaker in (
                    agent1_name,
                    agent1_role,
                    agent2_name,
                    agent2_role
                ):

                    final_message = message.get(
                        "message",
                        ""
                    )

                    break

            st.info(
                final_message
                if final_message
                else "Agreement successfully reached."
            )

        with result_col2:

            st.markdown("### 📊 Negotiation Summary")

            st.metric(
                "Rounds Completed",
                f"{st.session_state.simulation_round}/{max_rounds}"
            )

            st.metric(
                "Mode",
                "AI vs AI"
            )

            st.metric(
                "Participants",
                f"{agent1_name} ↔ {agent2_name}"
            )

    elif status == "Deadlock":

        st.warning(
            "⚠️ Negotiation ended without an agreement."
        )

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.metric(
                "Rounds Completed",
                f"{st.session_state.simulation_round}/{max_rounds}"
            )

        with result_col2:

            st.metric(
                "Status",
                "Deadlock"
            )

    elif status == "Maximum Rounds Reached":

        st.warning(
            "⚠️ Maximum negotiation rounds reached."
        )

        result_col1, result_col2 = st.columns(2)

        with result_col1:

            st.metric(
                "Rounds Completed",
                f"{st.session_state.simulation_round}/{max_rounds}"
            )

        with result_col2:

            st.metric(
                "Status",
                "Maximum Rounds Reached"
            )

    elif status == "Quota Exceeded":

        st.error(
            "⛔ Negotiation stopped because the Gemini API quota was exceeded."
        )

# ============================================================
# NEGOTIATION ANALYTICS
# ============================================================

if st.session_state.simulation_finished:

    st.divider()

    st.subheader("📊 Negotiation Analytics")

    messages = st.session_state.simulation_messages

    # --------------------------------------------------------
    # Collect negotiation messages
    # --------------------------------------------------------

    negotiation_messages = [
        message
        for message in messages
        if message.get("speaker") in (
            agent1_name,
            agent1_role,
            agent2_name,
            agent2_role
        )
    ]

    # --------------------------------------------------------
    # Smart monetary value extraction
    # --------------------------------------------------------

    import re


    def extract_money_values(text):

        values = []

        # ---------------------------------------------
        # ₹30 lakh / ₹30.5 lakh
        # ---------------------------------------------

        lakh_matches = re.findall(
            r"₹\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lakhs)",
            text,
            flags=re.IGNORECASE
        )

        for value in lakh_matches:

            value = value.replace(",", "")

            try:

                values.append(
                    float(value) * 100000
                )

            except ValueError:

                pass

        # ---------------------------------------------
        # ₹10 LPA / ₹12 LPA
        # ---------------------------------------------

        lpa_matches = re.findall(
            r"₹\s*([\d,]+(?:\.\d+)?)\s*LPA",
            text,
            flags=re.IGNORECASE
        )

        for value in lpa_matches:

            value = value.replace(",", "")

            try:

                values.append(
                    float(value) * 100000
                )

            except ValueError:

                pass

        # ---------------------------------------------
        # Normal ₹ amounts
        # Example:
        # ₹100,000
        # ₹97,500
        # ₹2,400,000
        # ---------------------------------------------

        normal_matches = re.findall(
            r"₹\s*([\d,]+(?:\.\d+)?)"
            r"(?!\s*(?:lakh|lakhs|LPA))",
            text,
            flags=re.IGNORECASE
        )

        for value in normal_matches:

            value = value.replace(",", "")

            try:

                values.append(
                    float(value)
                )

            except ValueError:

                pass

        return values


    # --------------------------------------------------------
    # Extract all monetary values from negotiation
    # --------------------------------------------------------

    extracted_values = []

    for message in negotiation_messages:

        text = message.get(
            "message",
            ""
        )

        values = extract_money_values(text)

        extracted_values.extend(values)


    # --------------------------------------------------------
    # Project Budget correction
    # --------------------------------------------------------
    # The opening Budget Allocator message contains the
    # TOTAL PROJECT BUDGET, e.g. ₹50 lakh.
    #
    # We don't want ₹50 lakh to become the department's
    # starting request.
    # --------------------------------------------------------

    if scenario == "Project Budget Allocation":

        filtered_values = []

        for message in negotiation_messages:

            speaker = message.get(
                "speaker",
                ""
            )

            text = message.get(
                "message",
                ""
            )

            # Skip the opening Budget Manager message
            # containing the total project budget.

            if (
                speaker == "Budget Allocator"
                and (
                    "total project budget" in text.lower()
                    or "total budget available" in text.lower()
                )
            ):

                continue

            filtered_values.extend(
                extract_money_values(text)
            )

        extracted_values = filtered_values



    # --------------------------------------------------------
    # Scenario-specific analytics
    # --------------------------------------------------------

    if scenario == "Vendor Pricing Negotiation":

        if extracted_values:

            starting_price = extracted_values[0]

            final_price = extracted_values[-1]

            price_difference = (
                starting_price - final_price
            )

            st.markdown(
                "### 💰 Pricing Analysis"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Starting Price",
                    f"₹{starting_price:,.0f}"
                )

            with col2:

                st.metric(
                    "Final Price",
                    f"₹{final_price:,.0f}"
                )

            with col3:

                st.metric(
                    "Price Difference",
                    f"₹{price_difference:,.0f}"
                )

    elif scenario == "Job Offer Negotiation":

        if extracted_values:

            starting_salary = extracted_values[0]

            final_salary = extracted_values[-1]

            salary_difference = (
                final_salary - starting_salary
            )

            st.markdown(
                "### 💼 Salary Analysis"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Initial Salary",
                    f"₹{starting_salary:,.0f}"
                )

            with col2:

                st.metric(
                    "Final Salary",
                    f"₹{final_salary:,.0f}"
                )

            with col3:

                st.metric(
                    "Salary Increase",
                    f"₹{salary_difference:,.0f}"
                )

    elif scenario == "Project Budget Allocation":

        if extracted_values:

            # Find the first actual Budget Requester proposal
            initial_budget = None

            for message in negotiation_messages:

                speaker = message.get("speaker", "")
                text = message.get("message", "")

                if speaker in (
                    "Budget Requester",
                    "Department Representative"
                ):

                    values = extract_money_values(text)

                    if values:
                        initial_budget = values[-1]
                        break

            # Fallback
            if initial_budget is None:
                initial_budget = extracted_values[0]

            final_budget = extracted_values[-1]

            budget_difference = (
                initial_budget - final_budget
            )

            st.markdown(
                "### 💰 Budget Analysis"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Initial Request",
                    f"₹{initial_budget:,.0f}"
                )

            with col2:

                st.metric(
                    "Final Allocation",
                    f"₹{final_budget:,.0f}"
                )

            with col3:

                st.metric(
                    "Difference",
                    f"₹{budget_difference:,.0f}"
                )

    # --------------------------------------------------------
    # General negotiation statistics
    # --------------------------------------------------------

    st.markdown(
        "### 📈 Negotiation Statistics"
    )

    stat1, stat2, stat3 = st.columns(3)

    with stat1:

        st.metric(
            "Rounds Completed",
            f"{st.session_state.simulation_round}/{max_rounds}"
        )

    with stat2:

        st.metric(
            "AI Turns",
            len(negotiation_messages)
        )

    with stat3:

        st.metric(
            "Outcome",
            status
        )
# ============================================================
# NEGOTIATION CONVERSATION
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

        speaker = message.get(
            "speaker",
            "AI Agent"
        )

        text = message.get(
            "message",
            ""
        )

        round_number = message.get(
            "round",
            None
        )

        if round_number:

            round_text = (
                f" • Round {round_number}"
            )

        else:

            round_text = ""

        # ==========================================
        # System message
        # ==========================================

        if speaker == "System":

            st.success(
                f"🤝 **System**{round_text}\n\n{text}"
            )

            continue

        # ==========================================
        # Determine which side the agent belongs to
        # ==========================================

        is_agent1 = (
            speaker == agent1_name
            or speaker == agent1_role
        )

        # ==========================================
        # Create one row for every message
        # ==========================================

        left_col, right_col = st.columns(
            [1, 1],
            gap="large"
        )

        # ==========================================
        # Agent 1 → LEFT
        # ==========================================

        if is_agent1:

            with left_col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🤖 {speaker}"
                    )

                    if round_text:

                        st.caption(
                            round_text.strip(" •")
                        )

                    st.write(text)

            # Empty right side

            with right_col:

                st.empty()

        # ==========================================
        # Agent 2 → RIGHT
        # ==========================================

        else:

            # Empty left side

            with left_col:

                st.empty()

            with right_col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🤖 {speaker}"
                    )

                    if round_text:

                        st.caption(
                            round_text.strip(" •")
                        )

                    st.write(text)


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

if (
    session_id
    and not st.session_state.simulation_finished
):

    time.sleep(1)

    st.rerun()


# ============================================================
# BOTTOM ACTIONS
# ============================================================

st.divider()

back_col, restart_col, report_col = st.columns(3)

with back_col:

    if st.button(
        "🏠 Back to Home",
        use_container_width=True
    ):

        st.session_state.simulation_finished = True

        st.switch_page(
            "pages/Home.py"
        )


with restart_col:

    if st.button(
        "🔄 Restart Simulation",
        use_container_width=True
    ):

        st.session_state.simulation_messages = []
        st.session_state.simulation_started = False
        st.session_state.simulation_finished = False
        st.session_state.simulation_round = 0
        st.session_state.simulation_status = "Waiting"
        st.session_state.active_agent = None
        st.session_state.waiting_for_response = False

        st.rerun()
        
with report_col:

    if st.button(
        "📊 View Report",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Reports.py"
        )