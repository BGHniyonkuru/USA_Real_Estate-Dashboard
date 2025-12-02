import streamlit as st

st.set_page_config(
    page_title="US Housing Affordability Dashboard",
    page_icon="house",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# === FIX FINAL : PLUS AUCUN ESPACE BLANC EN HAUT ===
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .main > div {
        padding-top: 0rem !important;
    }
    /* Cache le titre "Dashboard - Real Estate" qui apparaît seul */
    header + div > div:first-child,
    [data-testid="stHeader"] ~ div h1 {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


import Home
import Dashboard
import Prediction

if "page" not in st.session_state:
    st.session_state.page = "Home"

tabs = ["Home", "Dashboard", "Prediction"]
active_page = st.session_state.page

cols = st.columns(3)

for idx, tab_name in enumerate(tabs):
    with cols[idx]:
        if st.button(
            tab_name,
            key=tab_name,
            use_container_width=True,
            type="primary" if active_page == tab_name else "secondary"
        ):
            st.session_state.page = tab_name
            st.rerun()

# Style : barre bleue sous l'onglet actif + boutons jolis
active_idx = tabs.index(active_page)

st.markdown(f"""
<style>
    /* Barre bleue sous l'onglet actif */
    div[data-testid="column"]:nth-child({active_idx + 1}) {{
        position: relative;
    }}
    div[data-testid="column"]:nth-child({active_idx + 1})::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 10%;
        width: 80%;
        height: 4px;
        background-color: #1a73e8;
        border-radius: 2px;
    }}

    /* Boutons identiques et modernes */
    .stButton > button {{
        height: 56px !important;
        border-radius: 12px !important;
        font-size: 17px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }}
</style>
""", unsafe_allow_html=True)

if st.session_state.page == "Home":
    Home.run()
elif st.session_state.page == "Dashboard":
    view = st.sidebar.radio("Section", ["National Overview", "My Personal Opportunities"])
    with st.sidebar:
        st.header("Your Profile")
        salary = st.number_input("Your Annual Gross Income ($)", min_value=0, value=85000, step=5000)
        goal = st.selectbox("Goal", ["Buy", "Rent"], index=0 if st.session_state.get("goal", "Buy") == "Buy" else 1)
        horizon = st.slider("Time Horizon (years)", 1, 30, 5)
        
        if goal == "Buy":
            st.subheader("Mortgage Settings")
            down_payment_pct = st.slider("Down Payment (%)", 3.0, 50.0, 20.0, 0.5) / 100
            mortgage_rate = st.slider("Expected Mortgage Rate (%)", 3.0, 12.0, 7.0, 0.1) / 100
            st.info(f"Down Payment: {(down_payment_pct*100):.1f}%\nRate: {(mortgage_rate*100):.1f}%")
        else:
            down_payment_pct = 0.20
            mortgage_rate = 0.07

        # Sauvegarde dans session_state
        st.session_state.user_salary = salary
        st.session_state.goal = goal
        st.session_state.horizon = horizon
        st.session_state.down_payment_pct = down_payment_pct
        st.session_state.mortgage_rate = mortgage_rate
    if view == "National Overview":
        Dashboard.run_national()
    else:
        Dashboard.run_personal()
    
else: 
    st.session_state.current_page = "Prediction"
    Prediction.run()