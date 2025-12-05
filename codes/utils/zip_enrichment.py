# utils/zip_enrichment.py
import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_zip_to_city():
    csv_path = Path(__file__).parent.parent/"data_extracted" / "data" / "geo" / "uszips.csv"
    
    if not csv_path.exists():
        st.error(f"Fichier introuvable : {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path, usecols=['zip', 'city', 'state_id'], dtype={'zip': str})
    df['zip'] = df['zip'].str.zfill(5)
    
    df = df.rename(columns={
        'zip': 'ZIP',
        'city': 'City',
        'state_id': 'State'
    })
    
    df['City'] = df['City'].fillna("Unknown").str.title()
    
    return df