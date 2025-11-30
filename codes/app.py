# codes/app.py → just redirects to Home
import streamlit as st
st.set_page_config(page_title="US Housing Affordability", layout="wide")

# Simple sidebar navigation
page = st.sidebar.radio("Go to", ["Home", "Interactive Dashboard", "Prediction (coming soon)"])

if page == "Home":
    import Home
if page == "Interactive Dashboard":
    import Dashboard
if page == "Prediction (coming soon)":
    import Prediction
