import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
# --- Encabezado de la app ---
st.markdown("""
    <div style="display: flex; gap: 20px; margin-bottom: 20px;">
        <a href="/Corralones" target="_self">Corralones</a>
        <a href="/panel_de_usuario" target="_self">Panel de usuario</a>
        <a href="/registro_obra" target="_self">Registro de obra</a>
        <a href="/predictor" target="_self">Cálculo de materiales</a>
    </div>
""", unsafe_allow_html=True)

st.title("CIMIENTO FUTURO\n\n")
st.set_page_config(page_title="Precios Corralones", layout="wide")
st.subheader("Comparador de Precios - Corralones")

# ---------- SCRAPERS ----------
sitios = ["Easy", "ElAmigo", "Orlandisa"]
sitio = st.sidebar.selectbox("Seleccioná el corralón", sitios)
paginas = st.sidebar.slider("Número de páginas a scrapear", 1, 5, 2)

@st.cache_data()
def scrappear(sitio, paginas):
    productos = []
    if sitio == "Easy":
        for p in range(1, paginas + 1):
            url = f"https://www.easy.com.ar/construccion/construccion?page={p}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.product__card")
            for card in cards:
                nm = card.select_one("span.product__description--name")
                pr = card.select_one("span.price")
                if nm and pr:
                    productos.append({
                        "Producto": nm.text.strip(),
                        "Precio": pr.text.strip(),
                        "Tienda": "Easy"
                    })
    elif sitio == "ElAmigo":
        for p in range(1, paginas + 1):
            url = f"https://www.elamigo.com.ar/grueso?page={p}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".product-thumb")
            for card in cards:
                nm = card.select_one(".name")
                pr = card.select_one(".price")
                if nm and pr:
                    productos.append({
                        "Producto": nm.text.strip(),
                        "Precio": pr.text.strip(),
                        "Tienda": "ElAmigo"
                    })
    elif sitio == "Orlandisa":
        for p in range(1, paginas + 1):
            url = f"https://www.orlandisa.com/ecommerce/corralon-130?page={p}"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".product")
            for card in cards:
                nm = card.select_one(".product__title") or card.select_one(".name")
                pr = card.select_one(".price")
                if nm and pr:
                    productos.append({
                        "Producto": nm.text.strip(),
                        "Precio": pr.text.strip(),
                        "Tienda": "Orlandisa"
                    })
    return pd.DataFrame(productos)

df = scrappear(sitio, paginas)

if df.empty:
    st.warning("⚠️ No se encontraron productos. Probá con otro sitio o más páginas.")
else:
    # Mostrar filtro de tienda solo si la columna existe
    if "Tienda" in df.columns:
        tiendas_disponibles = df["Tienda"].unique().tolist()
        filtro = st.sidebar.multiselect("Filtrar por tienda", tiendas_disponibles, default=tiendas_disponibles)
        df = df[df["Tienda"].isin(filtro)]

    st.success(f"✅ Se encontraron {len(df)} productos.")
    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button("📥 Descargar CSV", csv, f"productos_{sitio.lower()}.csv", "text/csv")