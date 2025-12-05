# utils/data_loader.py

import pandas as pd
import streamlit as st
from pathlib import Path
import gdown
import zipfile

# --- CONFIG Google Drive ---
FILE_ID = "1DK5GpCeIlecHwYljoCpzGfCkUojCPKZL"
ZIP_URL = f"https://drive.google.com/uc?id={FILE_ID}"

# --- chemins locaux ---
ZIP_PATH = Path("data.zip")
EXTRACT_DIR = Path("data_extracted")
CSV_RELATIVE_PATH = Path("data/data_cleaned/affordability_zip.csv")  # chemin dans le ZIP


@st.cache_data(ttl=3600, show_spinner="Chargement des données...")
def load_affordability_data():
    """
    Télécharge le ZIP depuis Google Drive si nécessaire,
    l'extrait, puis charge le CSV 'affordability_zip.csv'.
    """

    # 1) Télécharger si le ZIP n'existe pas
    if not ZIP_PATH.exists():
        gdown.download(ZIP_URL, str(ZIP_PATH), quiet=False)

    # 2) Dézipper si non extrait
    target_csv_path = EXTRACT_DIR / CSV_RELATIVE_PATH

    if not target_csv_path.exists():
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

    # 3) Charger le CSV
    if not target_csv_path.exists():
        st.error(f"Fichier introuvable après extraction : {target_csv_path}")
        st.stop()

    df = pd.read_csv(target_csv_path)
    df['ZIP'] = df['ZIP'].astype(str).str.zfill(5)
    return df
