import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.luxauto.lu"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_search_page(make=None, model=None, page=1):
    params = {'page': page}
    if make:
        params['make'] = make
    if model:
        params['model'] = model
    res = requests.get(f"{BASE_URL}/fr/voitures/occasions-toutes-marques", headers=headers, params=params)
    res.raise_for_status()
    return res.text

def parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select('div.listing-card')
    data = []
    for card in cards:
        try:
            title = card.select_one('h3.listing-title').get_text(strip=True)
            price = int(card.select_one('div.price').get_text(strip=True).replace('€','').replace('.','').replace('\xa0',''))
            year, mileage = None, None
            for attr in card.select('div.listing-attribute'):
                txt = attr.get_text(strip=True)
                if 'km' in txt:
                    mileage = int(txt.replace('km','').replace('.','').replace('\xa0',''))
                elif txt.isdigit() and len(txt)==4:
                    year = int(txt)
            link = BASE_URL + card.select_one('a.listing-link')['href']
            data.append({'title': title, 'price': price, 'year': year, 'mileage': mileage, 'link': link})
        except:
            continue
    return data

def analyze_listings(listings, margin_pct):
    df = pd.DataFrame(listings)
    if df.empty:
        return df
    df['group'] = df['title'] + ' ' + df['year'].astype(str)
    df['avg_price'] = df.groupby('group')['price'].transform('mean')
    df['profit'] = df['avg_price'] - df['price']
    df['margin_pct'] = df['profit'] / df['price'] * 100
    return df[df['margin_pct'] >= margin_pct].sort_values(by='margin_pct', ascending=False)

st.title(\"🔍 Analyseur d'Annonces Luxauto\")

make = st.sidebar.text_input(\"Marque\", \"Renault\")
model = st.sidebar.text_input(\"Modèle\", \"Clio\")
pages = st.sidebar.slider(\"Nombre de pages à analyser\", 1, 10, 3)
margin = st.sidebar.slider(\"Marge minimale (%)\", 0, 50, 10)
delay = st.sidebar.slider(\"Délai entre les requêtes (s)\", 0.0, 5.0, 1.0)

if st.sidebar.button(\"Lancer l'analyse\"):

    all_listings = []
    for page in range(1, pages + 1):
        html = fetch_search_page(make, model, page)
        all_listings += parse_listings(html)
        time.sleep(delay)

    results = analyze_listings(all_listings, margin)
    
    if results.empty:
        st.warning(\"Aucune opportunité rentable trouvée.\")
    else:
        st.success(f\"{len(results)} opportunités trouvées ! 📈\")
        st.dataframe(results[['title', 'year', 'price', 'avg_price', 'margin_pct', 'link']])
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button(\"📥 Télécharger en CSV\", csv, \"opportunites.csv\", \"text/csv\")
