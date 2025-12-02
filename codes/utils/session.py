# utils/session.py
import streamlit as st
def init_session_state():
    if "user_salary" not in st.session_state:
        st.session_state.user_salary = 85000
    if "down_payment" not in st.session_state:
        st.session_state.down_payment = 20
    if "horizon" not in st.session_state:
        st.session_state.horizon = 5
    if "goal" not in st.session_state:
        st.session_state.goal = "Buy a home"