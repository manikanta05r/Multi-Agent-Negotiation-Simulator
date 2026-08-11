import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Login | Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Main page */
    .block-container {
        max-width: 520px !important;
        padding-top: 45px !important;
        padding-bottom: 30px !important;
        margin: auto !important;
    }

    /* Center everything */
    .logo-container {
        text-align: center;
        margin-bottom: 18px;
    }

    .login-title {
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        color: #202124;
        margin-bottom: 6px;
    }

    .login-subtitle {
        text-align: center;
        font-size: 14px;
        color: #777777;
        margin-bottom: 28px;
    }

    /* Input labels */
    .stTextInput label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #333333 !important;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 8px !important;
        min-height: 44px !important;
    }

    div[data-baseweb="input"] input {
        font-size: 14px !important;
    }

    /* Remember me */
    .stCheckbox {
        margin-top: -5px;
        margin-bottom: 10px;
    }

    .stCheckbox label {
        font-size: 13px !important;
        color: #555555 !important;
    }

    /* Buttons */
    div.stButton > button {
        width: 100%;
        height: 44px;
        border-radius: 8px;
        border: none;
        background: #4f46e5;
        color: white;
        font-size: 15px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background: #4338ca;
        color: white;
    }

    /* Create account text */
    .create-text {
        text-align: center;
        color: #777777;
        font-size: 13px;
        margin-top: 18px;
        margin-bottom: 5px;
    }

    /* Footer */
    .login-footer {
        text-align: center;
        color: #aaaaaa;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)




# ============================================================
# CENTERED LOGO
# ============================================================

logo_left, logo_center, logo_right = st.columns([1, 1, 1])

with logo_center:
    st.image(
        "assets/logo.png",
        width=90
    )


# ============================================================
# LOGIN TITLE
# ============================================================

st.markdown(
    """
    <div class="login-title">
        Login to Your Account
    </div>

    <div class="login-subtitle">
        Sign in to continue to your negotiation workspace
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EMAIL
# ============================================================

email = st.text_input(
    "Email",
    placeholder="Enter your email",
    key="login_email"
)


# ============================================================
# PASSWORD
# ============================================================

password = st.text_input(
    "Password",
    placeholder="Enter your password",
    type="password",
    key="login_password"
)


# ============================================================
# REMEMBER ME
# ============================================================

remember_me = st.checkbox(
    "Remember me",
    key="remember_me"
)


# ============================================================
# LOGIN BUTTON
# ============================================================

if st.button(
    "Login",
    use_container_width=True,
    key="login_button"
):

    if not email.strip():

        st.error("Please enter your email.")

    elif not password:

        st.error("Please enter your password.")

    else:

        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.switch_page("app.py")
        # Connect backend here later.
   


# ============================================================
# CREATE ACCOUNT
# ============================================================

st.markdown(
    """
    <div class="create-text">
        Don't have an account?
    </div>
    """,
    unsafe_allow_html=True
)

if st.button(
    "Create Account",
    use_container_width=True,
    key="create_account_button"
):

    st.info("Account registration will be connected to the backend.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="login-footer">
        Multi-Agent Negotiation Simulator<br>
        AI-powered negotiation platform
    </div>
    """,
    unsafe_allow_html=True
)