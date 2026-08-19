import streamlit as st
import requests

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

mode = st.session_state.get("mode", "AI vs AI")
role = st.session_state.get("role", None)
scenario = st.session_state.get("scenario", "Buyer vs Supplier")
max_rounds = st.session_state.get("max_rounds", 10)
session_id = st.session_state.get("session_id", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "practice_finished" not in st.session_state:
    st.session_state.practice_finished = False

if "practice_status" not in st.session_state:
    st.session_state.practice_status = "Waiting"

if "practice_round" not in st.session_state:
    st.session_state.practice_round = 0

if "simulation_finished" not in st.session_state:
    st.session_state.simulation_finished = False

if "simulation_status" not in st.session_state:
    st.session_state.simulation_status = "Waiting"

if "simulation_round" not in st.session_state:
    st.session_state.simulation_round = 0

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

if "simulation_thinking" not in st.session_state:
    st.session_state.simulation_thinking = False

if "simulation_active_agent" not in st.session_state:
    st.session_state.simulation_active_agent = None

if "practice_thinking" not in st.session_state:
    st.session_state.practice_thinking = False

if "practice_pending_offer" not in st.session_state:
    st.session_state.practice_pending_offer = None

if "practice_processing" not in st.session_state:
    st.session_state.practice_processing = False
# ==========================================
# Header
# ==========================================

st.title("💬 Live Negotiation")

st.write(f"### Scenario: {scenario}")

st.divider()

chat_col, status_col = st.columns([3, 1])

# ==========================================
# Chat Section
# ==========================================

with chat_col:

    st.subheader("🗨️ Negotiation Conversation")

        # =====================================
    # AI vs AI
    # =====================================

    if mode == "AI vs AI":

        st.info(
            "🤖 AI vs AI mode — autonomous negotiation"
        )

        # ---------------------------------
        # Load existing conversation
        # ---------------------------------

        if session_id and len(st.session_state.messages) == 0:

            try:

                response = requests.get(
                    f"http://127.0.0.1:8000/negotiation/{session_id}",
                    timeout=10
                )

                if response.status_code == 200:

                    data = response.json()

                    backend_messages = data.get(
                        "messages",
                        []
                    )

                    st.session_state.messages = [
                        (
                            msg.get("speaker", "AI"),
                            msg.get("message", "")
                        )
                        for msg in backend_messages
                        if msg.get("speaker") != "System"
                    ]

                    st.session_state.simulation_round = data.get(
                        "round",
                        0
                    )

            except Exception as e:

                st.error(
                    f"Unable to load negotiation.\n\n{e}"
                )

        # ---------------------------------
        # Display conversation
        # ---------------------------------

        ai_roles = [
            "Buyer",
            "Supplier",
            "Candidate",
            "HR Manager",
            "Budget Requester",
            "Budget Allocator",
            "AI"
        ]

        for sender, message in st.session_state.messages:

            if sender in ai_roles:

                with st.chat_message("assistant"):

                    st.write(
                        f"🤖 **{sender}:** {message}"
                    )

            else:

                with st.chat_message("assistant"):

                    st.write(
                        f"🤖 **{sender}:** {message}"
                    )

        # ---------------------------------
        # Finished
        # ---------------------------------

        if st.session_state.simulation_finished:

            if st.session_state.simulation_status == "agreement_reached":

                st.success(
                    "✅ Agreement Reached"
                )

            elif st.session_state.simulation_status == "deadlock":

                st.warning(
                    "⚠️ Negotiation ended due to Deadlock"
                )

            elif st.session_state.simulation_status == "max_rounds_reached":

                st.warning(
                    "⚠️ Maximum Rounds Reached"
                )

            elif st.session_state.simulation_status == "quota_exceeded":

                st.error(
                    "⛔ Gemini API Quota Exceeded"
                )

        # ---------------------------------
        # Start simulation
        # ---------------------------------

        elif not st.session_state.simulation_running:

            if st.button(
                "▶️ Start AI Negotiation",
                use_container_width=True
            ):

                st.session_state.simulation_running = True

                st.rerun()

        # ---------------------------------
        # Automatic AI turns
        # ---------------------------------

        else:

            import time

            # Show thinking state

            thinking_placeholder = st.empty()

            # Determine the next AI agent
            if scenario == "Vendor Pricing Negotiation":

                if len(st.session_state.messages) == 0:
                    active_agent = "Supplier"
                else:
                    last_speaker = st.session_state.messages[-1][0]
                    active_agent = (
                        "Buyer"
                        if last_speaker == "Supplier"
                        else "Supplier"
                    )

            elif scenario == "Job Offer Negotiation":

                if len(st.session_state.messages) == 0:
                    active_agent = "HR Manager"
                else:
                    last_speaker = st.session_state.messages[-1][0]
                    active_agent = (
                        "Candidate"
                        if last_speaker == "HR Manager"
                        else "HR Manager"
                    )

            elif scenario == "Project Budget Allocation":

                if len(st.session_state.messages) == 0:
                    active_agent = "Budget Allocator"
                else:
                    last_speaker = st.session_state.messages[-1][0]
                    active_agent = (
                        "Budget Requester"
                        if last_speaker == "Budget Allocator"
                        else "Budget Allocator"
                    )

            else:
                active_agent = "AI"

            st.session_state.simulation_active_agent = active_agent

            thinking_placeholder.info(
                f"🤔 **{active_agent} is thinking...**"
            )

            # Wait approximately 2 seconds

            time.sleep(2)

            try:

                response = requests.post(

                    "http://127.0.0.1:8000/simulate-next-turn",

                    json={
                        "session_id": session_id
                    },

                    timeout=120

                )

                if response.status_code == 200:

                    data = response.json()

                    # -----------------------------
                    # AI response
                    # -----------------------------

                    ai_speaker = data.get(
                        "speaker",
                        "AI"
                    )

                    ai_message = data.get(
                        "message",
                        ""
                    )

                    # -----------------------------
                    # Add response
                    # -----------------------------

                    if ai_message:

                        st.session_state.messages.append(
                            (
                                ai_speaker,
                                ai_message
                            )
                        )

                    # -----------------------------
                    # Update round
                    # -----------------------------

                    st.session_state.simulation_round = data.get(
                        "round",
                        st.session_state.simulation_round
                    )

                    # -----------------------------
                    # Update status
                    # -----------------------------

                    status = data.get(
                        "status",
                        "in_progress"
                    )

                    st.session_state.simulation_status = status

                    # -----------------------------
                    # Check completion
                    # -----------------------------

                    if status in [
                        "agreement_reached",
                        "deadlock",
                        "max_rounds_reached",
                        "quota_exceeded"
                    ]:

                        st.session_state.simulation_finished = True

                        st.session_state.simulation_running = False

                else:

                    st.error(
                        f"Backend Error: {response.text}"
                    )

                    st.session_state.simulation_running = False

            except Exception as e:

                st.error(
                    f"Backend Connection Error\n\n{e}"
                )

                st.session_state.simulation_running = False

            finally:

                thinking_placeholder.empty()

            # ---------------------------------
            # Rerun for next AI turn
            # ---------------------------------

            if not st.session_state.simulation_finished:

                st.rerun()

    # =====================================
    # Human vs AI
    # =====================================

    else:

        st.info(f"🎮 Practice Mode | Your Role: **{role}**")

        # =====================================
        # Load existing backend conversation
        # =====================================

        if session_id and len(st.session_state.messages) == 0:

            try:

                response = requests.get(
                    f"http://127.0.0.1:8000/negotiation/{session_id}",
                    timeout=10
                )

                if response.status_code == 200:

                    data = response.json()

                    backend_messages = data.get(
                        "messages",
                        []
                    )

                    st.session_state.messages = [
                        (
                            msg.get("speaker", "AI"),
                            msg.get("message", "")
                        )
                        for msg in backend_messages
                    ]

                    st.session_state.practice_round = data.get(
                        "round",
                        0
                    )

            except Exception as e:

                st.error(
                    f"Unable to load negotiation.\n\n{e}"
                )

        # Show conversation
        # ==========================================
        # Zig-Zag Negotiation Conversation
        # ==========================================

        for index, (sender, message) in enumerate(
            st.session_state.messages
        ):

            # ------------------------------------------
            # System message
            # ------------------------------------------

            if sender == "System":

                st.success(
                    f"🤝 **System**\n\n{message}"
                )

                continue

            # ------------------------------------------
            # Determine whether this is the user's role
            # ------------------------------------------

            is_user = sender == role

            # ------------------------------------------
            # Create two sides
            # ------------------------------------------

            left_col, right_col = st.columns(
                [1, 1],
                gap="large"
            )

            # ==========================================
            # USER → LEFT
            # ==========================================

            if is_user:

                with left_col:

                    with st.container(border=True):

                        st.markdown(
                            f"### 🧑 {sender}"
                        )

                        st.caption(
                            f"Round {index // 2 + 1}"
                        )

                        st.write(message)

                with right_col:

                    st.empty()

            # ==========================================
            # AI → RIGHT
            # ==========================================

            else:

                with left_col:

                    st.empty()

                with right_col:

                    with st.container(border=True):

                        st.markdown(
                            f"### 🤖 {sender}"
                        )

                        st.caption(
                            f"Round {index // 2 + 1}"
                        )

                        st.write(message)

        # Chat input
        # =====================================
        # Chat Input / Negotiation Control
        # =====================================

        if st.session_state.practice_finished:

            if st.session_state.practice_status == "agreement_reached":
                st.success(
                    "✅ Agreement Reached — Further offers are disabled."
                )

            elif st.session_state.practice_status == "deadlock":
                st.warning(
                    "⚠️ Negotiation ended due to Deadlock — Further offers are disabled."
                )

            elif st.session_state.practice_status == "max_rounds_reached":
                st.warning(
                    "⚠️ Maximum Rounds Reached — Further offers are disabled."
                )

            else:
                st.info(
                    "✅ Negotiation Completed — Further offers are disabled."
                )

        else:

            thinking_placeholder = st.empty()

            user_offer = st.chat_input(
                "Enter your offer...",
                disabled=st.session_state.practice_finished
            )

            if user_offer:

                # Show user message
                st.session_state.messages.append(
                    (role, user_offer)
                )

                st.session_state.practice_thinking = True

                thinking_placeholder.info(
                    "🤖 AI is thinking..."
                )


                try:
                    

                    response = requests.post(

                        "http://127.0.0.1:8000/next-round",

                        json={

                            "session_id": session_id,

                            "speaker": role,

                            "message": user_offer

                        },

                        timeout=120

                    )

                    if response.status_code == 200:

                        data = response.json()

                        # Add AI reply
                        ai_speaker = data.get(
                            "speaker",
                            "AI"
                        )

                        ai_message = data.get(
                            "message",
                            ""
                        )

                        st.session_state.practice_thinking = False
                        thinking_placeholder.empty()

                        st.session_state.messages.append(
                            (
                                ai_speaker,
                                ai_message
                            )
                        )
                        # ---------------------------------
                        # Update round
                        # ---------------------------------

                        st.session_state.practice_round = (
                            data.get(
                                "round",
                                st.session_state.practice_round
                            )
                        )

                        # ---------------------------------
                        # Check negotiation status
                        # ---------------------------------

                        status = data.get(
                            "status",
                            "in_progress"
                        )

                        st.session_state.practice_status = status

                        if status == "agreement_reached":

                            st.session_state.practice_finished = True

                            st.success(
                                "✅ Agreement Reached"
                            )

                        elif status == "deadlock":

                            st.session_state.practice_finished = True

                            st.warning(
                                "⚠️ Negotiation ended due to Deadlock"
                            )

                        elif status == "max_rounds_reached":

                            st.session_state.practice_finished = True

                            st.warning(
                                "⚠️ Maximum Rounds Reached"
                            )

                    else:

                        st.error(
                            response.text
                        )

                except Exception as e:

                    st.session_state.practice_thinking = False

                    st.error(
                        f"Backend Connection Error\n\n{e}"
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

    if mode == "AI vs AI":

        active_agent = st.session_state.simulation_active_agent

        if active_agent:

            st.info(
                f"🤔 **{active_agent}** is thinking..."
            )

        elif not st.session_state.simulation_finished:

            st.success(
                "🟢 Waiting for next AI turn"
            )

    if mode == "AI vs AI":
        rounds = st.session_state.simulation_round
    else:
        rounds = st.session_state.practice_round

    st.metric(
        "Rounds",
        f"{rounds}/{max_rounds}"
    )

    progress = min(
        rounds / max_rounds,
        1.0
    )

    st.progress(progress)

    if mode == "AI vs AI":

        if st.session_state.simulation_finished:

            if st.session_state.simulation_status == "agreement_reached":

                st.success("✅ Agreement Reached")

            elif st.session_state.simulation_status == "deadlock":

                st.warning("⚠️ Deadlock")

            elif st.session_state.simulation_status == "max_rounds_reached":

                st.warning("⚠️ Maximum Rounds Reached")

            elif st.session_state.simulation_status == "quota_exceeded":

                st.error("⛔ Gemini API Quota Exceeded")

        elif len(st.session_state.messages) == 0:

            st.info("Waiting to start")

        else:

            st.success("🟢 Negotiation Active")

    else:

        if st.session_state.practice_finished:

            if st.session_state.practice_status == "agreement_reached":

                st.success("✅ Agreement Reached")

            elif st.session_state.practice_status == "deadlock":

                st.warning("⚠️ Deadlock")

            elif st.session_state.practice_status == "max_rounds_reached":

                st.warning("⚠️ Maximum Rounds Reached")

        elif len(st.session_state.messages) == 0:

            st.info("Waiting to start")

        else:

            st.success("🟢 Negotiation Active")

st.divider()

# ==========================================
# Summary
# ==========================================

st.subheader("📄 Negotiation Summary")

st.info(f"""
### Current Negotiation

**Scenario:** {scenario}

**Mode:** {mode}

**Role:** {role}

Continue negotiating until an agreement or deadlock is reached.
""")

st.divider()

# ==========================================
# Navigation
# ==========================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "🔄 Restart Negotiation",
        use_container_width=True
    ):

        st.session_state.messages = []

        # Practice Mode reset
        st.session_state.practice_finished = False
        st.session_state.practice_status = "Waiting"
        st.session_state.practice_round = 0
        st.session_state.practice_thinking = False

        # AI vs AI reset
        st.session_state.simulation_finished = False
        st.session_state.simulation_status = "Waiting"
        st.session_state.simulation_round = 0
        st.session_state.simulation_running = False
        st.session_state.simulation_thinking = False
        st.session_state.simulation_active_agent = None

        st.rerun()

with col2:

    if st.button("📊 View Reports", use_container_width=True):

        st.switch_page("pages/Reports.py")

with col3:

    if st.button("🏠 Back to Home", use_container_width=True):

        st.session_state.messages = []
        st.session_state.mode = None
        st.session_state.role = None

        st.switch_page("pages/Home.py")