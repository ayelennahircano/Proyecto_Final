import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Precios Corralones", layout="wide")
st.title("CIMIENTO FUTURO")
st.subheader("Comparador de Precios - Corralones")

# --- Cierre de sesión ---
if st.session_state.get("logueado"):
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.query_params["page"] = "cuenta.py"
        st.rerun()

# --- Scraper con clases reales ---
@st.cache_data
def scrappear_actualizado():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    productos = []

    # Easy
    try:
        r = requests.get("https://www.easy.com.ar/construccion-y-maderas/obra-gruesa", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.vtex-product-summary-2-x-container")
        for card in cards:
            nombre = card.select_one("span.vtex-product-summary-2-x-productBrand")
            precio = card.select_one("span.sellingPriceDivSearch")
            if nombre and precio:
                productos.append({
                    "Producto": nombre.text.strip(),
                    "Precio": precio.text.strip(),
                    "Tienda": "Easy"
                })
    except Exception as e:
        st.warning(f"❌ Error en Easy: {e}")

    # El Amigo
    try:
        r = requests.get("https://www.elamigo.com.ar/grueso", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.vtex-product-summary-2-x-galleryItem")
        for card in cards:
            nombre = card.select_one("div.vtex-product-summary-2-x-nameContainer")
            precio = card.select_one("span.vtex-product-price-1-x-currencyContainer")
            if nombre and precio:
                productos.append({
                    "Producto": nombre.text.strip(),
                    "Precio": precio.text.strip(),
                    "Tienda": "ElAmigo"
                })
    except Exception as e:
        st.warning(f"❌ Error en El Amigo: {e}")

    # Orlandisa
    try:
        r = requests.get("https://www.orlandisa.com/ecommerce/corralon-130", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.conten_producto")
        for card in cards:
            nombre = card.select_one("div.nombre_producto")
            precio = card.select_one("div.precio_producto")
            if nombre and precio:
                productos.append({
                    "Producto": nombre.text.strip(),
                    "Precio": precio.text.strip(),
                    "Tienda": "Orlandisa"
                })
    except Exception as e:
        st.warning(f"❌ Error en Orlandisa: {e}")

    return pd.DataFrame(productos)

# --- Ejecutar scraping ---
df = scrappear_actualizado()

# --- Mostrar resultados ---
if df.empty:
    st.warning("⚠️ No se encontraron productos.")
else:
    tiendas = df["Tienda"].unique().tolist()
    filtro = st.multiselect("Filtrar por tienda", tiendas, default=tiendas)
    df = df[df["Tienda"].isin(filtro)]

    st.success(f"✅ Se encontraron {len(df)} productos.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Descargar CSV", csv, "productos_corralones.csv", "text/csv")
