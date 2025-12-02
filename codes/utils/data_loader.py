# utils/data_loader.py
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data(ttl=3600, show_spinner="Chargement des données...")
def load_affordability_data():
    # Chemin depuis racine
    base_path = Path(__file__).parents[2] / "data" / "data_cleaned" / "affordability_zip.csv"
    
    if not base_path.exists():
        st.error(f"Fichier manquant : {base_path}")
        st.stop()
    
    df = pd.read_csv(base_path)
    df['ZIP'] = df['ZIP'].astype(str).str.zfill(5)
    return df