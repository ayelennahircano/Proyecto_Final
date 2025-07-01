import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Precios Corralones", layout="wide")
st.title("CIMIENTO FUTURO\n\n")
st.subheader("Comparador de Precios - Corralones\n")

# --- Verificar sesión ---
if st.session_state.get("logueado"):
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.query_params["page"] = "cuenta.py"
        st.rerun()

# ---------- PARÁMETROS ----------
sitios_opciones = ["Easy", "ElAmigo", "Orlandisa"]
sitios_seleccionados = st.sidebar.multiselect("Seleccioná los corralones", sitios_opciones, default=sitios_opciones)
busqueda = st.sidebar.text_input("🔍 Buscar producto (ej: cemento, hierro)").strip().lower()

# ---------- SCRAPERS ----------
@st.cache_data(show_spinner="Cargando productos...")
def scrappear_sitio(sitio, paginas=3):
    productos = []
    headers = {"User-Agent": "Mozilla/5.0"}

    if sitio == "Easy":
        for p in range(1, paginas + 1):
            url = f"https://www.easy.com.ar/construccion-y-maderas/obra-gruesa?page={p}"
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.discoargentina-search-result-custom-1-x-galleryItem")
            for card in cards:
                nombre = card.select_one("span.vtex-product-summary-2-x-productBrand")
                precio = card.select_one("span.vtex-product-price-1-x-sellingPriceValue")
                if nombre and precio:
                    productos.append({
                        "Producto": nombre.text.strip(),
                        "Precio": precio.text.strip(),
                        "Tienda": "Easy"
                    })

    elif sitio == "ElAmigo":
        for p in range(1, paginas + 1):
            url = f"https://www.elamigo.com.ar/grueso?page={p}"
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.vtex-product-summary-2-x-element")
            for card in cards:
                nombre = card.select_one("span.vtex-product-summary-2-x-productBrand")
                precio = card.select_one("span.vtex-product-price-1-x-sellingPriceValue")
                if nombre and precio:
                    productos.append({
                        "Producto": nombre.text.strip(),
                        "Precio": precio.text.strip(),
                        "Tienda": "ElAmigo"
                    })

    elif sitio == "Orlandisa":
        for p in range(1, paginas + 1):
            url = f"https://www.orlandisa.com/ecommerce/corralon-130?page={p}"
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.conten_producto")
            for card in cards:
                nombre = card.select_one("h2")
                precio = card.select_one("span.precio")
                if nombre and precio:
                    productos.append({
                        "Producto": nombre.text.strip(),
                        "Precio": precio.text.strip(),
                        "Tienda": "Orlandisa"
                    })

    return pd.DataFrame(productos)

# ---------- CARGA MULTISITIO ----------
dfs = [scrappear_sitio(sitio) for sitio in sitios_seleccionados]
df_completo = pd.concat(dfs, ignore_index=True)

# ---------- FILTROS ----------
if df_completo.empty:
    st.warning("⚠️ No se encontraron productos. Probá con otros sitios.")
else:
    # Filtro por palabra clave
    if busqueda:
        df_completo = df_completo[df_completo["Producto"].str.lower().str.contains(busqueda)]

    # Filtro por tienda
    tiendas_disponibles = df_completo["Tienda"].unique().tolist()
    filtro = st.sidebar.multiselect("Filtrar por tienda", tiendas_disponibles, default=tiendas_disponibles)
    df_filtrado = df_completo[df_completo["Tienda"].isin(filtro)]

    st.success(f"✅ Se encontraron {len(df_filtrado)} productos.")
    st.dataframe(df_filtrado)

    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button("Descargar CSV", csv, "productos_combinados.csv", "text/csv")
