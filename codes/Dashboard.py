# codes/Dashboard.py → VERSION FINALE QUI MARCHE À 100%
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="US Real Estate 2025", layout="wide")
st.title("US Housing Affordability Dashboard")
st.markdown("### Analyse des tendances régionales – Données Zillow + IRS 2024")

# Chargement sécurisé
path = Path(__file__).parent.parent / "data" / "data_cleaned" / "affordability_zip.csv"
if not path.exists():
    st.error("Fichier manquant → crée data/data_cleaned/affordability_zip.csv")
    st.stop()

df = pd.read_csv(path)

# Conversion ZIP en string + nettoyage
df['ZIP'] = df['ZIP'].astype(str).str.zfill(5)
df['Date'] = pd.to_datetime(df['Date'])

# === ANALYSES RÉGIONALES ===
st.header("1. Top 10 des zones les plus chères vs les plus abordables")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Loyers les plus élevés")
    top_rent = df.nlargest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
    st.dataframe(top_rent.style.format({'ZORI': '${:,.0f}', 'Income_Needed_Rent': '${:,.0f}'}))

with col2:
    st.subheader("Loyers les plus bas")
    bottom_rent = df.nsmallest(10, 'ZORI')[['ZIP', 'Metro', 'StateName', 'ZORI', 'Income_Needed_Rent']]
    st.dataframe(bottom_rent.style.format({'ZORI': '${:,.0f}', 'Income_Needed_Rent': '${:,.0f}'}))

# === CARTE PAR ÉTAT ===
st.header("2. Affordabilité par État")
state_data = df.groupby('StateName').agg({
    'ZORI': 'median',
    'ZHVI': 'median',
    'Avg_AGI': 'median',
    'Income_Needed_Rent': 'median'
}).reset_index()
state_data['Affordability_Ratio'] = state_data['Avg_AGI'] / state_data['Income_Needed_Rent']

fig = px.choropleth(state_data,
                    locations='StateName',
                    locationmode='USA-states',
                    color='Affordability_Ratio',
                    scope="usa",
                    color_continuous_scale="RdYlGn",
                    title="Ratio d'abordabilité locative par État (vert = abordable, rouge = crise)",
                    labels={'Affordability_Ratio': 'Ratio Revenu/Rent'})
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

# === COMPARAISON MÉTROPOLES ===
st.header("3. Les grandes métropoles en 2025")
metros = ["New York-Newark-Jersey City, NY-NJ-PA", "Los Angeles-Long Beach-Anaheim, CA",
          "Houston-The Woodlands-Sugar Land, TX", "Chicago-Naperville-Elgin, IL-IN-WI",
          "Miami-Fort Lauderdale-Pompano Beach, FL", "San Francisco-Oakland-Berkeley, CA"]

metro_data = df[df['Metro'].isin(metros)].groupby(['Metro', 'StateName']).agg({
    'ZORI': 'median',
    'ZHVI': 'median',
    'Avg_AGI': 'median',
    'Income_Needed_Rent': 'median',
    'Income_Needed_Buy': 'median'
}).round(0).reset_index()

fig_bar = px.bar(metro_data.sort_values('Income_Needed_Rent', ascending=False),
                 x='Metro', y='Income_Needed_Rent',
                 text='Income_Needed_Rent',
                 title="Revenu annuel nécessaire pour louer (médian)")
fig_bar.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
fig_bar.update_layout(xaxis_tickangle=15)
st.plotly_chart(fig_bar, use_container_width=True)

# === SCATTER INTERACTIF ===
st.header("4. Qui peut encore acheter ?")
fig_scatter = px.scatter(df, x='Avg_AGI', y='Income_Needed_Buy',
                         size='ZHVI', color='StateName',
                         hover_name='ZIP',
                         hover_data=['Metro', 'ZORI'],
                         title="Revenu réel vs Revenu nécessaire pour acheter")
fig_scatter.add_hline(y=df['Avg_AGI'].median(), line_dash="dash", line_color="green",
                      annotation_text="Revenu médian US")
fig_scatter.add_vline(x=df['Avg_AGI'].median(), line_dash="dash", line_color="green")
st.plotly_chart(fig_scatter, use_container_width=True)

st.success("Well done! Explore more insights in the sidebar.")
st.balloons()