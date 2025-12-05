# Dashboard.py 
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_affordability_data
from utils.prediction_engine import calculate_monthly_payment, get_best_locations
from utils.session import init_session_state
from utils.user_profile import get_user_profile

# ---------------------------------------------------
# Utility converters
# ---------------------------------------------------
def to_float(x, default=0.0):
    try:
        return float(str(x).strip())
    except:
        return default

def to_int(x, default=5):
    try:
        return int(float(str(x).strip()))
    except:
        return default

# Initialize states + user profile
init_session_state()
get_user_profile()


# ===================================================
# ================  NATIONAL VIEW  ==================
# ===================================================
def run_national():

    # Load data INSIDE function (important!)
    df_raw = load_affordability_data()

    st.header("1. Top 10 Most Expensive vs Cheapest Areas")

    # 📌 Sliders — Only if useful here
    salary           = to_float(st.session_state.user_salary, 80000)
    goal             = str(st.session_state.goal or "Buy")
    horizon          = to_int(st.session_state.horizon)
    mortgage_rate    = to_float(st.session_state.mortgage_rate, 0.07)
    down_payment_pct = to_float(st.session_state.down_payment_pct, 0.20)

    # -------- Top 10 expensive / cheapest rent --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Highest Rents (ZORI)")
        top_rent = df_raw.nlargest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
        top_rent_display = top_rent.copy().round(0)
        st.dataframe(
            top_rent_display.style.format({
                'ZORI': '${:,.0f}',
                'Income_Needed_Rent': '${:,.0f}'
            }),
            use_container_width=True
        )

    with col2:
        st.subheader("Lowest Rents (ZORI)")
        bottom_rent = df_raw.nsmallest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
        bottom_rent_display = bottom_rent.copy().round(0)
        st.dataframe(
            bottom_rent_display.style.format({
                'ZORI': '${:,.0f}',
                'Income_Needed_Rent': '${:,.0f}'
            }),
            use_container_width=True
        )

    # -------- State Affordability --------
    st.markdown("---")
    st.header("2. Affordability by State")

    state_data = df_raw.groupby('StateName').agg({
        'ZORI': 'median',
        'ZHVI': 'median',
        'Avg_AGI': 'median',
        'Income_Needed_Rent': 'median',
        'Income_Needed_Buy': 'median'
    }).round(0).reset_index()

    state_data['Rent_Affordability_Ratio'] = (state_data['Avg_AGI'] / state_data['Income_Needed_Rent']).round(2)
    state_data['Buy_Affordability_Ratio']  = (state_data['Avg_AGI'] / state_data['Income_Needed_Buy']).round(2)

    fig = px.choropleth(
        state_data,
        locations='StateName',
        locationmode='USA-states',
        color='Rent_Affordability_Ratio',
        scope="usa",
        color_continuous_scale="RdYlGn",
        range_color=(0.5, 2.5),
        title="Rent Affordability Ratio by State (Higher = Better)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------- Major Metros Comparison --------
    st.markdown("---")
    st.header("3. Major Metropolitan Areas – 2025 Outlook")

    major_metros = [
        "New York-Newark-Jersey City, NY-NJ-PA",
        "Los Angeles-Long Beach-Anaheim, CA",
        "Chicago-Naperville-Elgin, IL-IN-WI",
        "Dallas-Fort Worth-Arlington, TX",
        "Houston-The Woodlands-Sugar Land, TX",
        "Washington-Arlington-Alexandria, DC-VA-MD-WV",
        "Miami-Fort Lauderdale-Pompano Beach, FL",
        "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
        "Atlanta-Sandy Springs-Alpharetta, GA",
        "Boston-Cambridge-Newton, MA-NH",
        "San Francisco-Oakland-Berkeley, CA",
        "Phoenix-Mesa-Chandler, AZ",
        "Seattle-Tacoma-Bellevue, WA"
    ]

    metro_summary = df_raw[df_raw['Metro'].isin(major_metros)].groupby('Metro').agg({
        'ZHVI': 'median',
        'ZORI': 'median',
        'Income_Needed_Buy': 'median',
        'Income_Needed_Rent': 'median',
        'Avg_AGI': 'median'
    }).round(0)

    # 2025 projection
    metro_summary['ZHVI_2025'] = (metro_summary['ZHVI'] * 1.04).round(0)
    metro_summary['ZORI_2025'] = (metro_summary['ZORI'] * 1.04).round(0)
    metro_summary = metro_summary.sort_values('Income_Needed_Buy', ascending=False)

    fig = px.bar(
        metro_summary.reset_index(),
        x='Metro',
        y='Income_Needed_Buy',
        text='Income_Needed_Buy',
        title="Annual Income Required to Buy (2024 → 2025 projection)"
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=30, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # -------- Scatter Affordability --------
    st.markdown("---")
    st.header("4. Who Can Still Afford to Buy? (National View)")

    df_sample = df_raw.sample(6000, random_state=42).copy()

    fig = px.scatter(
        df_sample,
        x='Avg_AGI',
        y='Income_Needed_Buy',
        size='ZHVI',
        color='StateName',
        hover_name='Metro',
        labels={
            'Avg_AGI': 'Household Income (IRS)',
            'Income_Needed_Buy': 'Income Required to Buy',
            'ZHVI': 'Home Price'
        },
        opacity=0.7
    )

    # 45° affordability line
    max_val = max(df_sample['Avg_AGI'].max(), df_sample['Income_Needed_Buy'].max()) * 1.15
    fig.add_scatter(x=[0, max_val], y=[0, max_val], mode='lines', line=dict(color='green', width=2))

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### What each bubble shows")
        st.caption("""
        • **X-axis** = Actual household income (IRS)  
        • **Y-axis** = Income needed to buy a home  
        • **Size** = Zillow home price (ZHVI)  
        • **Color** = State  
        """)

    with col2:
        st.markdown("### The green line = affordability frontier")
        st.caption("""
        • Below the line → households can afford to buy  
        • Above the line → homes are unaffordable  
        • It's the point where actual income = required income  
        """)

    with col3:
        affordable = len(df_raw[df_raw['Avg_AGI'] >= df_raw['Income_Needed_Buy']])
        total = len(df_raw)
        pct = 100 * affordable / total
        st.markdown("### Key national insight")
        st.caption(f"""
        Only **{affordable:,} ZIP codes** out of **{total:,}**  
        are affordable to the average household.  
        → That's **{pct:.1f}%** of the country.  
        """)



# ===================================================
# ===============  PERSONAL VIEW  ===================
# ===================================================
def run_personal():

    # ---------------------------------------------------
    # 📌 Load slider values FIRST (important)
    # ---------------------------------------------------
    salary           = to_float(st.session_state.user_salary)
    goal             = str(st.session_state.goal or "Buy")
    horizon          = to_int(st.session_state.horizon)
    mortgage_rate    = to_float(st.session_state.mortgage_rate)
    down_payment_pct = to_float(st.session_state.down_payment_pct)

    st.header(f"Best Places for Me – {goal}")

    # ---------------------------------------------------
    # Compute personalized ranking
    # ---------------------------------------------------
    df = get_best_locations(
        salary=salary,
        goal=goal,
        horizon=horizon,
        inflation_rate=0.04,
        down_payment_pct=down_payment_pct,
        mortgage_rate=mortgage_rate
    )

    eligible = df[df["Eligible_Future"]]

    if eligible.empty:
        st.error("No locations are affordable with your current income and goal.")
        return

    # Best location
    best = eligible.iloc[0]

    st.success(f"#1 BEST PLACE → **{best['Metro']}, {best['StateName']}**")

    # ---------------------------------------------------
    #  METRICS
    # ---------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("ZIP", int(best["ZIP"]))
    col2.metric(
        f"Est. {'Home Price' if goal=='Buy' else 'Annual Rent'} ({horizon} yrs)",
        f"${best['Asset_Price_Future']:,.0f}"
    )
    col3.metric("Required Income", f"${best['Income_Needed_Future']:,.0f}")

    if goal == "Buy":
        down_payment = best["Asset_Price_Future"] * down_payment_pct
        col4.metric("Down Payment", f"${down_payment:,.0f}")
    else:
        col4.metric("Affordability Margin", f"{best['Affordability_%']:.0f}%")

    # ---------------------------------------------------
    # Mortgage details (if buying)
    # ---------------------------------------------------
    if goal == "Buy":
        with st.expander("Detailed Mortgage Breakdown"):
            price = best["ZHVI_Future"]
            down = price * down_payment_pct
            loan = price - down
            monthly = calculate_monthly_payment(price)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Home Price 2025+", f"${price:,.0f}")
            c2.metric("Down Payment", f"${down:,.0f}")
            c3.metric("Loan Amount", f"${loan:,.0f}")
            c4.metric("Monthly Payment", f"${monthly:,.0f}")

    # ---------------------------------------------------
    # Top 20 table
    # ---------------------------------------------------
    top20 = eligible.head(20).copy()
    top20.insert(0, "Rank", range(1, len(top20) + 1))

    st.subheader("Top 20 Best Locations for You")
    st.dataframe(top20, use_container_width=True)

    # CSV export
    csv = eligible.head(100).to_csv(index=False).encode()
    st.download_button("Download My Top 100 Locations", csv, "best_places.csv")
