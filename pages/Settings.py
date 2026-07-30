import streamlit as st

from components.styles import load_css
from components.navbar import show_navbar

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

load_css()
show_navbar()

# ==========================================
# Header
# ==========================================

st.title("⚙️ Settings")

st.markdown("""
Customize the Multi-Agent Negotiation Simulator by configuring AI agents,
negotiation preferences, appearance, notifications, and backend settings.
""")

st.divider()

# ==========================================
# AI Configuration
# ==========================================

with st.expander("🤖 AI Agent Configuration", expanded=True):

    ai_model = st.selectbox(
        "AI Model",
        [
            "GPT-4",
            "Gemini",
            "Claude",
            "Llama"
        ]
    )

    buyer_temperature = st.slider(
        "Buyer Agent Temperature",
        0.0,
        1.0,
        0.7
    )

    seller_temperature = st.slider(
        "Seller Agent Temperature",
        0.0,
        1.0,
        0.7
    )

st.divider()

# ==========================================
# Negotiation Preferences
# ==========================================

with st.expander("🎯 Negotiation Preferences"):

    default_rounds = st.slider(
        "Default Maximum Rounds",
        5,
        20,
        10
    )

    agreement_threshold = st.slider(
        "Default Agreement Threshold (%)",
        50,
        100,
        80
    )

    auto_save = st.checkbox(
        "Automatically Save Negotiation Reports",
        value=True
    )

st.divider()

# ==========================================
# Appearance
# ==========================================

with st.expander("🎨 Appearance"):

    theme = st.selectbox(
        "Theme",
        [
            "Light",
            "Dark",
            "System Default"
        ]
    )

    animations = st.checkbox(
        "Enable Animations",
        value=True
    )

st.divider()

# ==========================================
# Notifications
# ==========================================

with st.expander("🔔 Notifications"):

    email = st.checkbox(
        "Email Notifications",
        value=True
    )

    desktop = st.checkbox(
        "Desktop Notifications",
        value=False
    )

st.divider()

# ==========================================
# Backend Configuration
# ==========================================

with st.expander("🌐 Backend Configuration"):

    backend_url = st.text_input(
        "Backend API URL",
        "http://localhost:8000"
    )

    api_key = st.text_input(
        "API Key",
        type="password"
    )

st.divider()

# ==========================================
# Save / Reset
# ==========================================

left, right = st.columns(2)

with left:

    if st.button(
        "💾 Save Settings",
        use_container_width=True
    ):
        st.success("Settings saved successfully!")

with right:

    if st.button(
        "🔄 Reset Settings",
        use_container_width=True
    ):
        st.warning("Settings reset to default values.")

st.divider()

if st.button(
    "🏠 Back to Home",
    use_container_width=True
):
    st.switch_page("pages/Home.py")