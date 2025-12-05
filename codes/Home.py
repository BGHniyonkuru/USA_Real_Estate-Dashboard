# Home.py
import streamlit as st
from utils.user_profile import get_user_profile


def run():
    st.title("US Housing Affordability Dashboard")
    st.markdown("### M2 MIASHS – Open Data Project | December 2025")
    st.subheader("Ready to find out where you can actually afford to live?")

    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1600", use_container_width=True)

    st.markdown("""
    ### Project Goal
    Visualize **home prices**, **rents**, and **true housing affordability** across the United States using the most granular open data available:
    - Zillow Research (ZHVI & ZORI)
    - IRS SOI Tax Statistics (real household income by ZIP)
    - BLS Occupational Employment (local wages)

    ### Key Innovation: Real Affordability Index
    For the **first time in a student open data project**, we answer the question:

    > **"Can people actually afford to live where they work?"**

    We compute:
    - Income needed to **rent** (≤30% of income – HUD standard)
    - Income needed to **buy** (20% down, 7% rate)
    → Then compare to **actual IRS-reported income** by ZIP code

    ### Core Metrics
    | Metric                  | Source     | Level     |
    |-------------------------|------------|-----------|
    | Home Value (ZHVI)       | Zillow     | ZIP/Metro |
    | Rent (ZORI)             | Zillow     | ZIP/Metro |
    | Household Income        | IRS        | ZIP       |
    | Required Income         | Calculated | ZIP       |
    | Affordability Ratio     | Calculated | ZIP       |

    Ready to explore? → Click **Interactive Dashboard** in the sidebar
    """)

    with st.expander("Methodology & Calculation Formulas", expanded=False):
        st.markdown("""
    ### Key Metrics & Formulas Used
    | Metric                        | Formula                                        | Notes                                    |
    |-------------------------------|------------------------------------------------|------------------------------------------|
    | Income Needed (Rent)          | `(ZORI × 12) / 0.30`                           | HUD 30% rule                             |
    | Income Needed (Buy)           | `(ZHVI × 0.80 × 0.07) / 0.30`                  | 20% down + 7% 30-yr rate                 |
    | Rent Affordability Ratio      | `Avg AGI / Income Needed (Rent)`               | < 1.0 → rent-burdened                    |
    | Years to Save 20% Downpayment | `(ZHVI × 0.20) / (Avg AGI × 0.10)`             | 10% savings rate                         |
    Data as of October/November 2024
        """)
        st.caption("Sources: Zillow Research • IRS SOI • HUD • Author calculations")

    get_user_profile()

    st.success("Go to **Interactive Dashboard** in the sidebar →")
