# codes/utils/filters.py
import streamlit as st

def apply_filters(df):
    st.sidebar.header("Smart Search")
    query = st.sidebar.text_input(
        "Search city, metro, ZIP, or state (e.g. Miami, 90210, California)",
        value="New York"
    ).strip()

    if not query:
        return df

    # Recherche insensible à la casse, avec gestion des NaN
    mask = (
        df['Metro'].astype(str).str.contains(query, case=False, na=False) |
        df['StateName'].astype(str).str.contains(query, case=False, na=False) |
        df['ZIP'].astype(str).str.contains(query, na=False)
    )

    filtered = df[mask]
    
    if filtered.empty:
        st.warning(f"No results for '{query}'. Showing national overview.")
        return df
    else:
        st.sidebar.success(f"{len(filtered):,} ZIP codes found")
        return filtered