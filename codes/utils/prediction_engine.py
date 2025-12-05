# utils/prediction_engine.py
import numpy as np
from utils.data_loader import load_affordability_data
from utils.zip_enrichment import load_zip_to_city
import streamlit as st

def calculate_monthly_payment(
    price: float,
    down_payment_pct: float = 0.20,
    rate: float = 0.07,
    years: int = 30,
    property_tax_rate: float = 0.012, 
    insurance_rate: float = 0.0035, 
    hoa_monthly: float = 150
) -> float:
    """
    Retourne le paiement mensuel total (PITI + HOA)
    """
    loan_amount = price * (1 - down_payment_pct)
    monthly_rate = rate / 12
    n_payments = years * 12
    if monthly_rate == 0:
        mortgage = loan_amount / n_payments
    else:
        mortgage = loan_amount * (
            monthly_rate * (1 + monthly_rate)**n_payments /
            ((1 + monthly_rate)**n_payments - 1)
        )
    tax = price * property_tax_rate / 12
    insurance = price * insurance_rate / 12
    return mortgage + tax + insurance + hoa_monthly

def income_needed_to_buy(
    price: float,
    down_payment_pct: float = 0.20,
    rate: float = 0.07
) -> float:
  

    monthly = calculate_monthly_payment(price, down_payment_pct, rate)
    return (monthly * 12) / 0.30

@st.cache_data(ttl=3600, show_spinner=False)
def get_best_locations(
    salary=85000,
    goal="Buy",
    horizon=5,
    inflation_rate=0.04,
    down_payment_pct=0.20,
    mortgage_rate=0.07
):
    # FORCE LE RECALCUL À CHAQUE CHANGEMENT MÊME MINIME
    salary = float(salary)
    goal = str(goal).strip()
    horizon = int(horizon)
    inflation_rate = float(inflation_rate)
    down_payment_pct = float(down_payment_pct)
    mortgage_rate = float(mortgage_rate)

    # CLÉ DE CACHE UNIQUE → on force avec tous les params
    # (Streamlit le fait déjà, mais on s'assure)
    df = load_affordability_data().copy()

    # --- Enrichissement ---
    city_map = load_zip_to_city()
    df = df.merge(city_map[['ZIP', 'City']], on='ZIP', how='left')
    df['City'] = df['City'].fillna("Rural Area").str.title()
    df['Metro'] = df['Metro'].fillna("Non-metropolitan area")
    df['Location'] = df['City'] + " (" + df['Metro'] + ")"

    # --- Projections ---
    df['ZHVI_Future'] = df['ZHVI'] * (1 + inflation_rate) ** horizon
    df['ZORI_Future_Annual'] = df['ZORI'] * 12 * (1 + inflation_rate) ** horizon

    # --- Calcul du revenu nécessaire (SÉCURISÉ) ---
    if goal == "Buy":
        df['Income_Needed_Future'] = df['ZHVI_Future'].apply(
            income_needed_to_buy,
            down_payment_pct=down_payment_pct,
            rate=mortgage_rate
        )
        df['Asset_Price_Future'] = df['ZHVI_Future']
    else:  # Rent OU tout autre cas (y compris "Buy a home", None, etc.)
        df['Income_Needed_Future'] = df['ZORI_Future_Annual'] / 0.30
        df['Asset_Price_Future'] = df['ZORI_Future_Annual']   # ← LIGNE CRUCIALE

    # --- Score & éligibilité ---
    df["Eligible_Future"] = salary >= df["Income_Needed_Future"]
    df["Affordability_%"] = (salary / df["Income_Needed_Future"]) * 100
    df["Score"] = df["Affordability_%"] * (1_000_000 / df["Asset_Price_Future"])

    return df.sort_values("Score", ascending=False).reset_index(drop=True)