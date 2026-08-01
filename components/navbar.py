import streamlit as st


def show_navbar():

    left, right = st.columns([1, 7])

    with left:
        st.image("assets/logo.png", width=110)

    with right:

        st.markdown(
            """
            <h1 style="
            margin-bottom:0;
            color:#0F172A;
            font-size:42px;
            font-weight:700;">
            Multi-Agent Negotiation Simulator
            </h1>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p style="
            color:#64748B;
            font-size:18px;
            margin-top:-8px;">
            🤖 AI-Powered Multi-Agent Negotiation Platform
            </p>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")