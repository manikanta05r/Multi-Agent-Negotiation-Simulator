import streamlit as st


def feature_card(title, description, icon, button_text="Start Scenario"):

    with st.container(border=True):

        # Centered Icon
        st.markdown(
            f"<h1 style='text-align:center;font-size:60px;'>{icon}</h1>",
            unsafe_allow_html=True
        )

        # Title
        st.markdown(
            f"<h3 style='text-align:center;color:#0F172A;'>{title}</h3>",
            unsafe_allow_html=True
        )

        # Description
        st.markdown(
            f"""
            <p style="
                text-align:center;
                color:#64748B;
                font-size:16px;
                min-height:70px;">
                {description}
            </p>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        st.button(
            button_text,
            use_container_width=True,
            key=title
        )