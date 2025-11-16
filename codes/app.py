# app.py (dans le dossier codes/)
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="USA Real Estate Dashboard", layout="wide")
st.title("Dashboard - Real Estate USA")

# --- CHARGEMENT DES DONNÉES (CHEMIN CORRIGÉ) ---
@st.cache_data
def load_data():
    path = '../data/data_cleaned/'  # ← CORRIGÉ : on sort du dossier codes/
    files = {
        'afford_zip': 'affordability_zip.csv',
        'housing_zip': 'housing_zip_clean.csv',
        'mapping': 'zip_metro_mapping.csv',
        'afford_metro': 'affordability_metro.csv',
        'bls_agg': 'bls_metro_agg.csv'
    }
    data = {}
    for key, file in files.items():
        full_path = os.path.join(path, file)
        if os.path.exists(full_path):
            data[key] = pd.read_csv(full_path)
        else:
            st.error(f"Fichier manquant : {file} → Vérifiez le chemin : {full_path}")
            st.stop()
    return data

data = load_data()
afford_zip = data['afford_zip']
housing_zip = data['housing_zip']
mapping = data['mapping']
afford_metro = data['afford_metro']
bls_agg = data['bls_agg']


# --- FILTRES ---
st.sidebar.header("Filtres")
zip_list = st.sidebar.multiselect("Code Postal (ZIP)", sorted(afford_zip['ZIP'].unique())[:100])
metro_list = st.sidebar.multiselect("Métropole", sorted(afford_metro['Metro'].dropna().unique()))

# Filtrer
df_zip = afford_zip.copy()
if zip_list: df_zip = df_zip[df_zip['ZIP'].isin(zip_list)]
if metro_list: df_zip = df_zip[df_zip['Metro'].isin(metro_list)]

# --- CARTE ---
st.subheader("Carte - Accessibilité par ZIP")
m = folium.Map(location=[39.8, -98.5], zoom_start=4, tiles="CartoDB positron")
sample = df_zip.sample(min(300, len(df_zip)))
for _, row in sample.iterrows():
    if pd.notna(row['ZHVI']) and pd.notna(row['Avg_AGI']):
        ratio = row['Affordability_Ratio']
        color = "red" if ratio > 100 else "orange" if ratio > 70 else "green"
        folium.CircleMarker(
            location=[39.8, -98.5],
            radius=6, color=color, fill=True,
            popup=f"ZIP: {row['ZIP']}<br>ZHVI: ${row['ZHVI']:,.0f}<br>Ratio: {ratio:.1f}%"
        ).add_to(m)
st_folium(m, width=700, height=500)

# --- GRAPHIQUES ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Évolution ZHVI")
    plot_data = housing_zip[housing_zip['ZIP'].isin(zip_list[:5])] if zip_list else housing_zip.sample(5)
    fig1 = px.line(plot_data, x='Date', y='ZHVI', color='ZIP')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Revenu nécessaire vs Salaire")
    fig2 = px.scatter(afford_metro, x='Median_Wage_Metro', y='Income_Needed_Buy',
                      size='Afford_Ratio_vs_Wage', color='Metro')
    st.plotly_chart