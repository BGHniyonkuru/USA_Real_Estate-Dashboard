import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data(ttl=3600, show_spinner="Chargement des données...")
def load_affordability_data():
    base_path = Path(__file__).parent / "data" / "data_cleaned" / "affordability_zip.csv"
    
    if not base_path.exists():
        st.error(f"Fichier introuvable :\n{base_path}")
        st.stop()
    
    try:
        df = pd.read_csv(base_path)
        df['ZIP'] = df['ZIP'].astype(str).str.zfill(5)
        st.success(f"Données chargées : {len(df):,} ZIP codes")
        return df
    except Exception as e:
        st.error(f"Erreur lecture CSV : {e}")
        st.stop()