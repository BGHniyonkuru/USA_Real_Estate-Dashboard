# utils/charts.py
import streamlit as st
import plotly.express as px
import pandas as pd

state_codes = {
    'California': 'CA', 'New York': 'NY', 'Texas': 'TX', 'Florida': 'FL',
    'Illinois': 'IL', 'Pennsylvania': 'PA', 'Ohio': 'OH', 'Georgia': 'GA',
    'North Carolina': 'NC', 'Michigan': 'MI', 'New Jersey': 'NJ', 'Virginia': 'VA',
    'Washington': 'WA', 'Arizona': 'AZ', 'Massachusetts': 'MA', 'Tennessee': 'TN',
    'Indiana': 'IN', 'Missouri': 'MO', 'Maryland': 'MD', 'Wisconsin': 'WI',
    'Colorado': 'CO', 'Minnesota': 'MN', 'South Carolina': 'SC', 'Alabama': 'AL',
    'Louisiana': 'LA', 'Kentucky': 'KY', 'Oregon': 'OR', 'Oklahoma': 'OK',
    'Connecticut': 'CT', 'Utah': 'UT', 'Iowa': 'IA', 'Nevada': 'NV'
}

def kpi_row(df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Median Home Price", f"${df['ZHVI'].median():,.0f}", help="Zillow ZHVI")
    with col2:
        st.metric("Median Rent", f"${df['ZORI'].median():,.0f}", help="Zillow ZORI")
    with col3:
        st.metric("Median Income", f"${df['Avg_AGI'].median():,.0f}", help="IRS tax data")
    with col4:
        ratio = (df['Income_Needed_Rent'] / df['Avg_AGI']).median()
        st.metric("Rent Affordability Ratio", f"{ratio:.2f}x",
                  delta="Good" if ratio < 0.33 else "High" if ratio < 0.5 else "Critical",
                  help="Required income ÷ Actual income. Ideal < 0.30")

def map_us_states(df):
    st.subheader("Median Rent by State")
    state_df = df.groupby('StateName')['ZORI'].median().reset_index()
    state_df['code'] = state_df['StateName'].map(state_codes)
    
    fig = px.choropleth(state_df, locations='code', locationmode='USA-states',
                        color='ZORI', scope="usa", color_continuous_scale="Reds",
                        hover_name='StateName', labels={'ZORI': 'Median Rent'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def top_expensive_areas(df):
    st.subheader("Top 15 Most Expensive Areas (Rent)")
    top = df.nlargest(15, 'ZORI')[['Metro', 'ZIP', 'ZORI', 'StateName']]
    fig = px.bar(top, x='ZORI', y='Metro', orientation='h', text='ZORI', color='StateName',
             height=500)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_traces(texttemplate='$%{text:,.0f}')
    st.plotly_chart(fig, use_container_width=True)

def affordability_scatter(df):
    st.subheader("Affordability: Required vs Actual Income")
    fig = px.scatter(df, x='Avg_AGI', y='Income_Needed_Rent',
                     size='ZHVI', color='StateName', hover_name='Metro',
                     hover_data=['ZIP'], labels={
                         'Avg_AGI': 'Actual Income (IRS)',
                         'Income_Needed_Rent': 'Income Needed to Rent'
                     })
    max_val = max(df['Avg_AGI'].max(), df['Income_Needed_Rent'].max()) * 1.1
    fig.add_scatter(x=[0, max_val], y=[0, max_val], mode='lines',
                    line=dict(color='green', dash='dash'), name="Affordable")
    st.plotly_chart(fig, use_container_width=True)

def data_table(df):
    st.subheader("Detailed Data")
    cols = ['ZIP', 'Metro', 'StateName', 'ZHVI', 'ZORI', 'Avg_AGI', 'Income_Needed_Rent']
    display = df[cols].head(200).round(0)
    display.columns = ['ZIP', 'Metro', 'State', 'Home Price', 'Rent', 'Income', 'Needed (Rent)']
    st.dataframe(display.sort_values('Rent', ascending=False), use_container_width=True)