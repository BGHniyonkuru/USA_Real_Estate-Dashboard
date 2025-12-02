# Prediction.py
import streamlit as st
from utils.data_loader import load_affordability_data
from utils.prediction_engine import get_best_locations
from utils.session import init_session_state
from utils.user_profile import get_user_profile

df_raw = load_affordability_data()

def run():
    get_user_profile()  
    goal = st.session_state.goal


    st.title("Long-Term Forecast (2025–2035) – Where Will You Win?")

    salary = st.session_state.user_salary
    goal = st.session_state.goal
    horizon = st.session_state.horizon
    down_payment_pct = st.session_state.get("down_payment_pct", 0.20)

    # Slider inflation
    inflation = st.slider(
        "Estimated annual housing inflation (%)",
        min_value=1.0,
        max_value=12.0,
        value=4.5,
        step=0.5
    ) / 100

    df = get_best_locations(
        salary=salary,
        goal=goal,
        horizon=horizon,
        inflation_rate=inflation,
        down_payment_pct=down_payment_pct
    )

    
    eligible = df[df["Eligible_Future"]]

    if eligible.empty:
        st.error("No location is affordable under this scenario.")
        st.info("Try lowering inflation, increasing salary, or reducing down payment.")
        st.stop()

    st.success(f"**{len(eligible):,} locations** still affordable in **{2025 + horizon}**")

    winner = eligible.iloc[0]
    st.markdown(f"""
    ### Future Winner → **{winner['Location']}**  
    Estimated price/rent in {2025 + horizon}: **${winner['Asset_Price_Future']:,.0f}**  
    Required income: **${winner['Income_Needed_Future']:,.0f}** → **{winner['Affordability_%']:.0f}% margin**
    """)

    top15 = eligible.head(15).copy()
    top15.insert(0, "Rank", range(1, len(top15) + 1))

    if goal == "Buy":
        top15['ROI_5y_%'] = (((top15['Asset_Price_Future'] / top15['ZHVI']) ** (1/5) - 1) * 100).round(1)
    else:
        top15['ROI_5y_%'] = round(inflation * 100, 1)

    st.dataframe(
        top15[["Rank", "Location", "Metro", "StateName",
               "Asset_Price_Future", "Income_Needed_Future",
               "Affordability_%", "ROI_5y_%"]].round(0).style.format({
            "Asset_Price_Future": "${:,.0f}",
            "Income_Needed_Future": "${:,.0f}",
            "Affordability_%": "{:.0f}%",
            "ROI_5y_%": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption("ROI 5y = average annual price/rent appreciation over 5 years • Data: Zillow Research • Author calculations")