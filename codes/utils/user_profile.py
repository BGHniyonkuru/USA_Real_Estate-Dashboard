# utils/user_profile.py
import streamlit as st

def get_user_profile():
    """
    Initialise les valeurs par défaut et affiche tous les paramètres utilisateur.
    C'est le SEUL endroit où on lit et écrit dans session_state.
    """

    # === 1. Valeurs par défaut (si non initialisées) ===
    defaults = {
        "user_salary": 85000,
        "goal": "Buy",
        "horizon": 5,
        "down_payment_pct": 0.20,
        "mortgage_rate": 0.07
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # === 2. Sidebar – Profil utilisateur ===
    with st.sidebar:
        st.header("Your Profile")

        # Salaire annuel
        st.session_state.user_salary = st.number_input(
            "Your Annual Gross Income ($)",
            min_value=30_000,
            max_value=1_000_000,
            value=int(st.session_state.user_salary),
            step=5_000,
            help="Salaire brut annuel en dollars US",
            key="user_salary_input_sidebar"       # clé UNIQUE
        )

        # Objectif : Buy ou Rent
        st.session_state.goal = st.selectbox(
            "Goal",
            options=["Buy", "Rent"],
            index=0 if st.session_state.goal == "Buy" else 1,
            help="Souhaitez-vous acheter ou louer ?",
            key="goal_select"
        )

        # Horizon
        st.session_state.horizon = st.slider(
            "Time Horizon (years)",
            min_value=1,
            max_value=30,
            value=int(st.session_state.horizon),
            help="Dans combien d'années voulez-vous être installé ?",
            key="horizon_slider"
        )

        # ============ BUY MODE ===============
        if st.session_state.goal == "Buy":
            st.subheader("Mortgage Settings")

            dp_percent = st.slider(
                "Down Payment (%)",
                min_value=3,
                max_value=50,
                value=int(st.session_state.down_payment_pct * 100),
                step=1,
                key="dp_slider"
            )
            st.session_state.down_payment_pct = dp_percent / 100

            rate_percent = st.slider(
                "Expected Mortgage Rate (%)",
                min_value=3.0,
                max_value=12.0,
                value=round(st.session_state.mortgage_rate * 100, 1),
                step=0.1,
                key="rate_slider"
            )
            st.session_state.mortgage_rate = rate_percent / 100

            st.info(
                f"**Down Payment:** {dp_percent}%\n\n"
                f"**Mortgage Rate:** {rate_percent:.1f}%"
            )

        # ============ RENT MODE ===============
        else:
            st.subheader("Rental Settings")
            st.success("No down payment or mortgage rate needed for renting")
            st.caption("We use standard market rent + your chosen inflation rate")

            # For RENT mode: force defaults
            st.session_state.down_payment_pct = 0.20
            st.session_state.mortgage_rate = 0.07
