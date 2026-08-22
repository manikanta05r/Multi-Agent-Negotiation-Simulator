import streamlit as st

from database.connection import supabase


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Create Account | Multi-Agent Negotiation Simulator",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ============================================================
# CSS
# ============================================================

st.markdown(
     """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
 
    <style>
 
    :root {
        --brand-accent: #ff4d4d;
        --brand-blue: #3b82f6;
        --brand-text: #0f172a;
        --brand-muted: #64748b;
    }
 
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
 
    .stApp {
        background-color: #f8fafc;
        background-image:
            radial-gradient(circle at 10% 10%, rgba(59, 130, 246, 0.06) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(255, 77, 77, 0.06) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.04) 0%, transparent 60%);
        background-attachment: fixed;
    }
 
    section[data-testid="stSidebar"] {
        display: none;
    }
 
    /* Hide Streamlit default chrome */
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
 
    .block-container {
        max-width: 550px;
        padding-top: 4rem;
        padding-bottom: 4rem;
    }
 
    /* Header */
    h1 {
        text-align: center;
        color: var(--brand-text);
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2.25rem !important;
        letter-spacing: -0.02em;
        animation: fadeInUp 0.6s ease-out forwards;
    }
 
    .subtitle {
        text-align: center;
        color: var(--brand-muted);
        font-weight: 500;
        font-size: 0.9rem;
        max-width: 320px;
        margin: 0 auto 2.5rem auto;
    }
 
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
 
    /* Input labels */
    .stTextInput label {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        transition: color 0.2s ease;
    }
 
    .stTextInput:focus-within label {
        color: var(--brand-blue) !important;
    }
 
    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 16px !important;
        min-height: 52px !important;
        background: rgba(248, 250, 252, 0.6) !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.2s ease;
    }
 
    div[data-baseweb="input"] input {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--brand-text) !important;
    }
 
    div[data-baseweb="input"]:focus-within {
        border: 1px solid var(--brand-blue) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08) !important;
        background: #ffffff !important;
    }
 
    /* Form card — glassy, rounded, floating */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.08);
        animation: fadeInUp 0.6s ease-out 0.1s forwards;
    }
 
    /* Gradient CTA button (submit) */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        border: none;
        border-radius: 16px;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0.9rem 0;
        color: white;
        background: linear-gradient(135deg, #3b82f6 0%, #2dd4bf 100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 20px -8px rgba(59, 130, 246, 0.4);
    }
 
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px -6px rgba(59, 130, 246, 0.4);
        filter: brightness(1.05);
        color: white;
    }
 
    /* Secondary "Login" button below the form */
    div[data-testid="stVerticalBlock"] > div:last-child div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2dd4bf 100%);
        color: white;
        border: 2px solid #f1f5f9;
        box-shadow: none;
    }
 
    div[data-testid="stVerticalBlock"] > div:last-child div.stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2dd4bf 100%);
        border-color: #e2e8f0;
        
    }
 
    hr {
        border-color: #e2e8f0 !important;
    }
 
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    "<h1>🤝 Create Account</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Create your account to access the Multi-Agent Negotiation Simulator.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CREATE ACCOUNT FORM
# ============================================================

with st.form("create_account_form"):

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
    )

    verify_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
    )

    create_account_button = st.form_submit_button(
        "Create Account",
        use_container_width=True,
    )


# ============================================================
# ACCOUNT CREATION
# ============================================================

if create_account_button:

    email = email.strip().lower()

    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    if not email:
        st.error("Please enter your email address.")
        st.stop()

    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    if not password:
        st.error("Please enter a password.")
        st.stop()

    # --------------------------------------------------------
    # Validate password confirmation
    # --------------------------------------------------------

    if password != verify_password:
        st.error("Passwords do not match.")
        st.stop()

    # --------------------------------------------------------
    # Validate password length
    # --------------------------------------------------------

    if len(password) < 6:
        st.error("Password must contain at least 6 characters.")
        st.stop()

    try:

        # ====================================================
        # CREATE USER IN SUPABASE AUTH
        # ====================================================

        auth_response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        # ====================================================
        # CHECK USER CREATION
        # ====================================================

        if not auth_response.user:

            st.error(
                "Unable to create account."
            )

            st.stop()

        # ====================================================
        # STORE AUTH USER INFORMATION
        # ====================================================

        st.session_state.user_id = auth_response.user.id
        st.session_state.user_email = auth_response.user.email

        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            "Account created successfully!"
        )

        # ----------------------------------------------------
        # Email confirmation may be enabled
        # ----------------------------------------------------

        if auth_response.session is None:

            st.info(
                "Please check your email and confirm your account "
                "before logging in."
            )

        else:

            st.info(
                "Your account is ready. You can now log in."
            )

        # ====================================================
        # GO TO LOGIN
        # ====================================================

        st.switch_page("pages/login.py")

    except Exception as e:

        error_message = str(e)
        error_lower = error_message.lower()

        # ----------------------------------------------------
        # Existing account
        # ----------------------------------------------------

        if (
            "already registered" in error_lower
            or "user already exists" in error_lower
            or "already been registered" in error_lower
        ):

            st.error(
                "An account with this email already exists."
            )

        # ----------------------------------------------------
        # Email rate limit
        # ----------------------------------------------------

        elif "rate limit" in error_lower:

            st.error(
                "Supabase email rate limit exceeded. "
                "Please wait before trying again."
            )

        # ----------------------------------------------------
        # Invalid email
        # ----------------------------------------------------

        elif "invalid email" in error_lower:

            st.error(
                "Please enter a valid email address."
            )

        # ----------------------------------------------------
        # Other errors
        # ----------------------------------------------------

        else:

            st.error(
                f"Account creation failed: {error_message}"
            )


# ============================================================
# LOGIN LINK
# ============================================================

st.markdown("---")

st.markdown(
    "<div style='text-align:center;'>Already have an account?</div>",
    unsafe_allow_html=True,
)

if st.button(
    "Login",
    use_container_width=True,
):

    st.switch_page("pages/login.py")