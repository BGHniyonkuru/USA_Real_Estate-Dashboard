# utils/user_profile.py
import streamlit as st

def get_user_profile():
    defaults = {
        "user_salary": 85000,
        "goal": "Buy",          
        "horizon": 5,
        "down_payment_pct": 0.20,
        "mortgage_rate": 0.07
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    with st.sidebar:
        st.header("Your Profile")

        st.session_state.user_salary = st.number_input(
            "Your Annual Gross Income ($)",
            min_value=30000, max_value=1000000, value=int(st.session_state.user_salary), step=5000
        )

        st.session_state.goal = st.selectbox(
            "Goal", ["Buy", "Rent"],
            index=0 if st.session_state.goal == "Buy" else 1
        )

        st.session_state.horizon = st.slider(
            "Time Horizon (years)", 1, 30, int(st.session_state.horizon)
        )

        if st.session_state.goal == "Buy":
            st.subheader("Mortgage Settings")
            dp = st.slider("Down Payment (%)", 3, 50, int(st.session_state.down_payment_pct * 100))
            rate = st.slider("Expected Mortgage Rate (%)", 3.0, 12.0, round(st.session_state.mortgage_rate * 100, 1), 0.1)

            st.session_state.down_payment_pct = dp / 100
            st.session_state.mortgage_rate = rate / 100

            st.info(f"Down Payment: {dp}%\nRate: {rate}%")

        else:
            st.subheader("Rental Settings")
            st.success("No down payment or mortgage rate needed for renting")
            st.caption("We assume standard market rent + 4% annual inflation")

            st.session_state.down_payment_pct = 0.20
            st.session_state.mortgage_rate = 0.07