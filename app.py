# redeploy trigger

import streamlit as st
import requests

BASE_URL = "https://www.luxauto.lu/fr/voitures/occasions-toutes-marques"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_raw_html(make=None, model=None, page=1):
    params = {'page': page}
    if make:
        params['make'] = make
    if model:
        params['model'] = model
    res = requests.get(BASE_URL, headers=headers, params=params)
    res.raise_for_status()
    return res.text

st.title("🛠️ Test HTML brut - Luxauto")

make = st.text_input("Marque (facultatif)", "")
model = st.text_input("Modèle (facultatif)", "")
page = st.number_input("Page", min_value=1, value=1)

if st.button("📥 Récupérer HTML"):
    try:
        html = fetch_raw_html(make or None, model or None, page)
        st.code(html[:3000], language='html')  # on affiche uniquement les 3000 premiers caractères
        st.success("✅ HTML récupéré avec succès. Copie-le ici dans le chat pour que je corrige le parseur.")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {e}")
