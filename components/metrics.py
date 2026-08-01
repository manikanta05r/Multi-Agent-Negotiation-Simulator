import streamlit as st


def dashboard_metrics():

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🤝 Total Negotiations",
            value="128",
            delta="+12 Today"
        )

    with col2:
        st.metric(
            label="✅ Agreements",
            value="102",
            delta="+8"
        )

    with col3:
        st.metric(
            label="🤖 AI Agents",
            value="2",
            delta="Buyer | Seller"
        )

    with col4:
        st.metric(
            label="📈 Success Rate",
            value="79.6%",
            delta="+3%"
        )