# Dashboard.py 
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_affordability_data
from utils.prediction_engine import *
from utils.session import init_session_state
from utils.user_profile import get_user_profile

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

init_session_state()
get_user_profile()  
goal = st.session_state.goal

salary           = to_float(st.session_state.user_salary, 80000)
goal             = str(st.session_state.goal or "Buy")
horizon          = to_int(st.session_state.horizon)           
mortgage_rate    = to_float(st.session_state.mortgage_rate, 0.07)
down_payment_pct = to_float(st.session_state.down_payment_pct, 0.20)

df_raw = load_affordability_data()

def run_national():
    st.header("1. Top 10 Most Expensive vs Cheapest Areas")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Highest Rents (ZORI)")
        top_rent = df_raw.nlargest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
        top_rent_display = top_rent.copy()
        top_rent_display['ZORI'] = top_rent_display['ZORI'].round(0)
        top_rent_display['Income_Needed_Rent'] = top_rent_display['Income_Needed_Rent'].round(0)
        st.dataframe(
            top_rent_display.style.format({
                'ZORI': '${:,.0f}',
                'Income_Needed_Rent': '${:,.0f}'
            }).set_caption("Top 10 Most Expensive Rental Markets"),
            use_container_width=True
        )

    with col2:
        st.subheader("Lowest Rents (ZORI)")
        bottom_rent = df_raw.nsmallest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
        bottom_rent_display = bottom_rent.copy()
        bottom_rent_display['ZORI'] = bottom_rent_display['ZORI'].round(0)
        bottom_rent_display['Income_Needed_Rent'] = bottom_rent_display['Income_Needed_Rent'].round(0)
        st.dataframe(
            bottom_rent_display.style.format({
                'ZORI': '${:,.0f}',
                'Income_Needed_Rent': '${:,.0f}'
            }).set_caption("Top 10 Most Affordable Rental Markets"),
            use_container_width=True
        )

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

    # =============================================
    # 3. Major Metros Comparison (2025 projection)
    # =============================================
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

    # 2025 projection (4% annual inflation × 1 year)
    metro_summary['ZHVI_2025'] = (metro_summary['ZHVI'] * 1.04).round(0)
    metro_summary['ZORI_2025'] = (metro_summary['ZORI'] * 1.04).round(0)

    metro_summary = metro_summary.sort_values('Income_Needed_Buy', ascending=False)

    fig = px.bar(
        metro_summary.reset_index(),
        x='Metro',
        y='Income_Needed_Buy',
        text='Income_Needed_Buy',
        title="Annual Income Required to Buy (2024 → 2025 projection)",
        labels={"Income_Needed_Buy": "Income Needed to Buy"}
    )
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(xaxis_tickangle=30, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # 4. Who Can Still Afford to Buy? → Version 100% dynamique & pédagogique
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
        hover_data={
            'ZIP': True,
            'ZHVI': ':$,.0f',
            'ZORI': ':$,.0f',
            'Avg_AGI': ':$,.0f',
            'Income_Needed_Buy': ':$,.0f',
            'StateName': False,  
            'Metro': False       
        },
        labels={
            'Avg_AGI': 'Actual Household Income (IRS)',
            'Income_Needed_Buy': 'Income Required to Buy<br>(20% down • 7% rate • 30 years)',
            'ZHVI': 'Home Price',
            'StateName': 'State'
        },
        color_discrete_sequence=px.colors.qualitative.Vivid,
        opacity=0.7
    )

    
    max_val = max(df_sample['Avg_AGI'].max(), df_sample['Income_Needed_Buy'].max()) * 1.15
    fig.add_scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        line=dict(color='#00D4AA', width=5),
        name='Affordable threshold',
        hoverinfo='skip'
    )

    median_income = df_raw['Avg_AGI'].median()
    fig.add_vline(
        x=median_income,
        line=dict(color="#FF6B00", dash="dash", width=3),
        annotation_text=f"US Median Income<br>${median_income:,.0f}",
        annotation_position="top left"
    )

    fig.update_layout(
        height=720,
        showlegend=False,
        xaxis=dict(tickformat='$,', title_font_size=14),
        yaxis=dict(tickformat='$,', title_font_size=14),
        hoverlabel=dict(bgcolor="white", font_size=13),
        title=None
    )

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**What each bubble shows**")
        st.caption("""
        • Size = average home price (ZHVI)  
        • Position X = real income in this ZIP (IRS)  
        • Position Y = income needed to buy  
        • Color = state
        """)

    with col2:
        st.markdown("**Green line = affordability frontier**")
        st.success("Below = households can afford to buy")
        st.error("Above = homes are unaffordable for average residents")

    with col3:
        st.markdown("**Key insight (2025)**")
        st.warning(f"""
        Only **{len(df_raw[df_raw['Avg_AGI'] >= df_raw['Income_Needed_Buy']]):,} out of {len(df_raw):,} ZIP codes**  
        are still affordable for the average household  
        → **{100 * len(df_raw[df_raw['Avg_AGI'] >= df_raw['Income_Needed_Buy']]) / len(df_raw):.1f}%** of America
        """)

    st.caption("Data: Zillow Research (Oct 2024) • IRS SOI (2022) • 7% mortgage rate • 20% down payment")
def run_personal():
    st.header(f"Best Places for Me – {goal}")

    df = get_best_locations(
        salary=salary,
        goal=goal,
        horizon=horizon,
        down_payment_pct=down_payment_pct,
        mortgage_rate=mortgage_rate
    )

    eligible = df[df["Eligible_Future"]]

    if eligible.empty:
        st.error("No locations are affordable with your current income and goal")
        st.info("Try switching to 'Rent' or increasing your salary in the sidebar")
        return

    eligible = df[df["Eligible_Future"]]
    if eligible.empty:
        st.error("No locations are affordable with your current income and goal")
        st.info("Try switching to 'Rent' or increasing your salary in the sidebar")
        return

    best = eligible.iloc[0]

    st.success(f"#1 BEST PLACE FOR YOU → **{best['Metro']}, {best['StateName']}**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ZIP Code", int(best["ZIP"]))
    col2.metric(f"Est. {'Home Price' if goal=='Buy' else 'Annual Rent'} ({horizon} yrs)", 
                f"${best['Asset_Price_Future']:,.0f}")

    if goal == "Buy":
        col3.metric("Required Income", f"${best['Income_Needed_Future']:,.0f}")
        col4.metric("Down Payment (20%)", f"${best['Down_Payment_Required']:,.0f}")
    else:
        col3.metric("Required Income", f"${best['Income_Needed_Future']:,.0f}")
        col4.metric("Affordability Margin", f"{best['Affordability_%']:.0f}%")

    # Détail mortgage
    if goal == "Buy":
        with st.expander("Detailed Mortgage Breakdown", expanded=True):
            price = best['ZHVI_Future']
            down = best['Down_Payment_Required']
            loan = price - down
            monthly = calculate_monthly_payment(price)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Home Price 2025+", f"${price:,.0f}")
            c2.metric("20% Down Payment", f"${down:,.0f}", 
                    delta=f"{(down/salary)*100:.1f}% of your salary" if salary > 0 else None)
            c3.metric("Loan Amount", f"${loan:,.0f}")
            c4.metric("Est. Monthly Payment", f"${monthly:,.0f}")
            
            st.caption("Includes: principal + interest (7%) + property tax (1.2%) + insurance (0.35%) + HOA (~$150)")
   
    top20 = eligible.head(20).copy()
    top20.insert(0, "Rank", range(1, len(top20) + 1))


    top20 = top20[[
        "Rank", "Location", "Metro", "StateName",
        "ZHVI", "ZORI", "Asset_Price_Future",
        "Income_Needed_Future", "Affordability_%"
    ]].round(0)

    top20.columns = [
        "Rank",
        "Location",
        "Metro Area",
        "State",
        "Current Home Price",
        "Current Monthly Rent",
        "Est. Price/Rent in 5 yrs",
        "Required Income (future)",
        "Affordability Margin %"
    ]


    st.dataframe(
        top20.style.format({
            "Current Home Price": "${:,.0f}",
            "Current Monthly Rent": "${:,.0f}",
            "Est. Price/Rent in 5 yrs": "${:,.0f}",
            "Required Income (future)": "${:,.0f}",
            "Affordability Margin %": "{:.0f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    csv = eligible.head(100).to_csv(index=False).encode()
    st.download_button("Download My Top 100 Locations", csv, "my_best_places.csv")

    with st.expander("How are these metrics calculated?", expanded=False):
        st.markdown("""
        | Metric                        | Explanation                                                                                  | Formula                                           |
        |-------------------------------|----------------------------------------------------------------------------------------------|---------------------------------------------------|
        | Current Home Price            | Zillow Home Value Index (ZHVI)                                                               | Raw Zillow data                                   |
        | Current Monthly Rent          | Zillow Observed Rent Index (ZORI)                                                            | Raw Zillow data                                   |
        | Est. Price/Rent in X years    | Projected using 4% annual inflation (default)                                                | Current × (1.04)^years                            |
        | Required Income (future)      | Income needed to buy/rent without spending >30% of gross income                              | Based on HUD 30% rule + mortgage math             |
        | Affordability Margin %        | 100% = you earn exactly what's needed → 200% = very comfortable                             | (Your Salary ÷ Required Income) × 100             |
        | Strategic Score               | Higher = better combination of affordability + low cost                                      | Margin % × (1,000,000 ÷ Future Price)             |
        """)
        st.caption("Data: Zillow Research • IRS SOI • HUD Guidelines • Author calculations")

