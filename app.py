import uuid

import streamlit as st

from components.styles import load_css
from components.navbar import show_navbar
from database.connection import get_supabase_client, is_supabase_available
from database.models import NegotiationMessage, NegotiationSession
from database.operations import add_message, create_session

st.set_page_config(
    page_title="Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

show_navbar()

left, right = st.columns([2, 1], gap="large")

with left:

    st.title("Welcome to the Multi-Agent Negotiation Simulator")

    st.write(
        "An AI-powered platform that enables intelligent agents to negotiate in real-world business scenarios."
    )

    st.subheader("Key Features")

    st.markdown("""
- 🤖 AI Agent Negotiation
- 💬 Live Negotiation Simulation
- 📊 Interactive Dashboard
- 📄 Automatic Report Generation
- ⚡ Multiple Negotiation Scenarios
""")

    st.button("🚀 Start New Negotiation", type="primary")

with right:

    st.info("""
### Supported Scenarios

🛒 Buyer vs Supplier

💼 HR vs Candidate

💰 Budget Allocation

⚙️ Custom Negotiation
""")

st.divider()

st.subheader("Database Status")

if is_supabase_available():
    st.success("Supabase connection is configured and ready.")
else:
    st.warning("Supabase is not configured yet. Set SUPABASE_URL and SUPABASE_ANON_KEY to enable database storage.")

st.subheader("Platform Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Negotiations", "0")
c2.metric("Agreements", "0")
c3.metric("AI Agents", "0")
c4.metric("Reports", "0")

if st.button("Save demo negotiation to database"):
    client = get_supabase_client()
    if client is None:
        st.error("Database is not available. Check your Supabase environment variables.")
    else:
        session = NegotiationSession(
            id=str(uuid.uuid4()),
            scenario="Buyer vs Supplier",
            mode="demo",
            role="buyer",
            status="in_progress",
            metadata={"source": "streamlit-demo"},
        )
        created_session = create_session(session)
        if created_session:
            message = NegotiationMessage(
                session_id=session.id,
                speaker="system",
                message="Demo negotiation saved to Supabase",
            )
            add_message(message)
            st.success("Demo negotiation saved to the database.")
        else:
            st.error("The demo record could not be created.")

st.divider()

st.subheader("About")

st.write("""
The Multi-Agent Negotiation Simulator enables multiple AI agents to negotiate
under different business scenarios.

The application consists of:

• Streamlit Frontend

• FastAPI Backend

• AI Agents

• Gemini LLM

• MongoDB Database
""")