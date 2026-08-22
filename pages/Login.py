import streamlit as st

from database.connection import supabase


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Login | Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap"
        rel="stylesheet"
    >

    <style>

    /* ========================================================
       ROOT VARIABLES
    ======================================================== */

    :root {
        --brand-accent: #ff4d4d;
        --brand-blue: #3b82f6;
        --brand-teal: #2dd4bf;
        --brand-text: #0f172a;
        --brand-muted: #64748b;
    }


    /* ========================================================
       GLOBAL FONT
    ======================================================== */

    html,
    body,
    [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }


    /* ========================================================
       PAGE BACKGROUND
    ======================================================== */

    .stApp {
        background-color: #f8fafc;

        background-image:
            radial-gradient(
                circle at 10% 10%,
                rgba(59, 130, 246, 0.06) 0%,
                transparent 40%
            ),
            radial-gradient(
                circle at 90% 90%,
                rgba(255, 77, 77, 0.06) 0%,
                transparent 40%
            ),
            radial-gradient(
                circle at 50% 50%,
                rgba(139, 92, 246, 0.04) 0%,
                transparent 60%
            );

        background-attachment: fixed;
    }


    /* ========================================================
       HIDE SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        display: none;
    }


    /* ========================================================
       HIDE STREAMLIT CHROME
    ======================================================== */

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       MAIN CONTAINER
    ======================================================== */

    .block-container {
        max-width: 550px;
        padding-top: 4rem;
        padding-bottom: 4rem;
    }


    /* ========================================================
       HEADER
    ======================================================== */

    .login-title {
        text-align: center;

        color: var(--brand-text);

        font-family: 'Space Grotesk', sans-serif !important;

        font-weight: 700;

        font-size: 2.25rem;

        letter-spacing: -0.02em;

        margin-bottom: 0.35rem;
    }


    /* ========================================================
       SUBTITLE
    ======================================================== */

    .login-subtitle {
        text-align: center;

        color: var(--brand-muted);

        font-weight: 500;

        font-size: 0.9rem;

        max-width: 350px;

        margin: 0 auto 2.5rem auto;
    }


    /* ========================================================
       FORM CARD
       ONLY THE FORM IS ANIMATED
    ======================================================== */

    div[data-testid="stForm"] {

        background: rgba(255, 255, 255, 0.8);

        backdrop-filter: blur(20px);

        -webkit-backdrop-filter: blur(20px);

        padding: 2.5rem;

        border-radius: 2.5rem;

        border: 1px solid rgba(255, 255, 255, 0.6);

        box-shadow:
            0 25px 50px -12px rgba(0, 0, 0, 0.08);

        opacity: 0;

        transform: translateY(18px);

        animation:
            formFadeIn
            0.5s
            ease-out
            0.1s
            forwards;
    }


    /* ========================================================
       FORM ANIMATION
    ======================================================== */

    @keyframes formFadeIn {

        from {
            opacity: 0;
            transform: translateY(18px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }

    }


    /* ========================================================
       INPUT LABELS
    ======================================================== */

    .stTextInput label {

        font-size: 11px !important;

        font-weight: 700 !important;

        color: #94a3b8 !important;

        text-transform: uppercase;

        letter-spacing: 0.08em;

        transition: color 0.2s ease;
    }


    /* ========================================================
       LABEL WHEN INPUT IS FOCUSED
    ======================================================== */

    .stTextInput:focus-within label {

        color: var(--brand-blue) !important;
    }


    /* ========================================================
       INPUT BOX
    ======================================================== */

    div[data-baseweb="input"] {

        border-radius: 16px !important;

        min-height: 52px !important;

        background: rgba(248, 250, 252, 0.6) !important;

        border: 1px solid #e2e8f0 !important;

        transition:
            all 0.2s ease;
    }


    /* ========================================================
       INPUT TEXT
    ======================================================== */

    div[data-baseweb="input"] input {

        font-size: 14px !important;

        font-weight: 600 !important;

        color: var(--brand-text) !important;
    }


    /* ========================================================
       INPUT FOCUS
    ======================================================== */

    div[data-baseweb="input"]:focus-within {

        border: 1px solid var(--brand-blue) !important;

        box-shadow:
            0 0 0 4px
            rgba(59, 130, 246, 0.08) !important;

        background: #ffffff !important;
    }


    /* ========================================================
       REMEMBER ME
    ======================================================== */

    .stCheckbox {

        margin-top: 8px;

        margin-bottom: 12px;
    }


    .stCheckbox label {

        font-size: 13px !important;

        font-weight: 500 !important;

        color: #64748b !important;

        text-transform: none !important;

        letter-spacing: normal !important;
    }


    /* ========================================================
       PRIMARY LOGIN BUTTON
    ======================================================== */

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {

        width: 100%;

        border: none;

        border-radius: 16px;

        font-weight: 700;

        font-size: 0.95rem;

        padding: 0.9rem 0;

        color: white;

        background:
            linear-gradient(
                135deg,
                #3b82f6 0%,
                #2dd4bf 100%
            );

        transition:
            all 0.3s
            cubic-bezier(0.4, 0, 0.2, 1);

        box-shadow:
            0 10px 20px -8px
            rgba(59, 130, 246, 0.4);
    }


    /* ========================================================
       BUTTON HOVER
    ======================================================== */

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {

        transform: translateY(-2px);

        box-shadow:
            0 12px 24px -6px
            rgba(59, 130, 246, 0.4);

        filter: brightness(1.05);

        color: white;
    }


    /* ========================================================
       CREATE ACCOUNT TEXT
    ======================================================== */

    .create-text {

        text-align: center;

        color: #64748b;

        font-size: 13px;

        font-weight: 500;

        margin-top: 22px;

        margin-bottom: 8px;
    }


    /* ========================================================
       DIVIDER
    ======================================================== */

    hr {

        border-color: #e2e8f0 !important;

        margin-top: 28px;

        margin-bottom: 22px;
    }


    /* ========================================================
       SECONDARY CREATE ACCOUNT BUTTON
    ======================================================== */

    .create-account-button div.stButton > button {

        background: white !important;

        color: #3b82f6 !important;

        border: 1px solid #dbeafe !important;

        box-shadow: none !important;

        transition: all 0.2s ease;
    }


    .create-account-button div.stButton > button:hover {

        background: #eff6ff !important;

        border-color: #93c5fd !important;

        color: #2563eb !important;

        transform: translateY(-1px);
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .login-footer {

        text-align: center;

        color: #94a3b8;

        font-size: 12px;

        line-height: 1.6;

        margin-top: 28px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="login-title">
        Welcome Back
    </div>

    <div class="login-subtitle">
        Sign in to continue to your negotiation workspace.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN FORM
# ============================================================

with st.form("login_form"):

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
        key="login_email",
    )

    password = st.text_input(
        "Password",
        placeholder="Enter your password",
        type="password",
        key="login_password",
    )

    remember_me = st.checkbox(
        "Remember me",
        key="remember_me",
    )

    login_button = st.form_submit_button(
        "Login",
        use_container_width=True,
    )


# ============================================================
# LOGIN
# ============================================================

if login_button:

    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    if not email.strip():

        st.error("Please enter your email.")

        st.stop()


    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    if not password:

        st.error("Please enter your password.")

        st.stop()


    try:

        # ====================================================
        # SUPABASE AUTHENTICATION
        # ====================================================

        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": email.strip().lower(),
                "password": password,
            }
        )


        # ====================================================
        # LOGIN SUCCESSFUL
        # ====================================================

        if auth_response.user:

            user = auth_response.user

            # ------------------------------------------------
            # Store authenticated user
            # ------------------------------------------------

            st.session_state.logged_in = True

            st.session_state.user_email = user.email

            st.session_state.user_id = user.id


            # ------------------------------------------------
            # Store Supabase session
            # ------------------------------------------------

            if auth_response.session:

                st.session_state.access_token = (
                    auth_response.session.access_token
                )

                st.session_state.refresh_token = (
                    auth_response.session.refresh_token
                )


            st.success("Login successful!")

            # ------------------------------------------------
            # Go to application
            # ------------------------------------------------

            st.switch_page("app.py")


        else:

            st.error(
                "Invalid email or password."
            )


    # ========================================================
    # LOGIN FAILED
    # ========================================================

    except Exception as e:

        error_message = str(e).lower()


        # ----------------------------------------------------
        # Invalid credentials
        # ----------------------------------------------------

        if (
            "invalid login credentials" in error_message
            or "invalid credentials" in error_message
        ):

            st.error(
                "Invalid email or password."
            )


        # ----------------------------------------------------
        # Email not confirmed
        # ----------------------------------------------------

        elif "email not confirmed" in error_message:

            st.error(
                "Please confirm your email before logging in."
            )


        # ----------------------------------------------------
        # Other errors
        # ----------------------------------------------------

        else:

            st.error(
                f"Login failed: {e}"
            )


# ============================================================
# CREATE ACCOUNT
# ============================================================

st.markdown(
    """
    <div class="create-text">
        Don't have an account?
    </div>
    """,
    unsafe_allow_html=True,
)


# Wrapper for secondary button styling
st.markdown(
    '<div class="create-account-button">',
    unsafe_allow_html=True,
)

if st.button(
    "Create Account",
    use_container_width=True,
    key="create_account_button",
):

    st.switch_page("pages/CreateAccount.py")

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


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
    unsafe_allow_html=True,
)