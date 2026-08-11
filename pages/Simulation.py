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
# AUTOMATIC BACKEND NEGOTIATION
# ============================================================

if (
    session_id
    and not st.session_state.simulation_started
):

    try:

        st.session_state.simulation_status = "Negotiating"
        st.session_state.active_agent = agent1_name

        response = requests.post(
            "http://127.0.0.1:8000/simulate-negotiation",
            json={
                "session_id": session_id
            },
            timeout=300
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.simulation_started = True

            messages = data.get(
                "conversation",
                []
            )

            st.session_state.simulation_messages = messages

            status = data.get(
                "status",
                "running"
            )

            rounds = data.get(
                "rounds_completed",
                0
            )

            st.session_state.simulation_round = rounds

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

            st.error(
                f"Backend error: {response.text}"
            )

            st.session_state.simulation_started = True
            st.session_state.simulation_finished = True

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to backend.\n\n{e}"
        )

        st.session_state.simulation_started = True
        st.session_state.simulation_finished = True


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

            st.info(
                "🟡 Thinking..."
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

            st.info(
                "🟡 Thinking..."
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
# NEGOTIATION INFORMATION
# ============================================================

st.divider()

info1, info2, info3 = st.columns(3)

with info1:

    st.metric(
        "Current Round",
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

    for message in st.session_state.simulation_messages:

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

        with st.chat_message("assistant"):

            st.markdown(
                f"**🤖 {speaker}**{round_text}"
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

back_col, restart_col = st.columns(2)

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

        st.rerun()