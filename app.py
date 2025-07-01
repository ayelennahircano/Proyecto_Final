import streamlit as st
import os
import base64

# --- Función para codificar imagen como base64 ---
@st.cache_data
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Usar imagen local como fondo ---
img_base64 = get_img_as_base64("background.png")  # Usá la imagen que descargaste o generaste

# --- Estilo CSS para fondo completo ---
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}}

[data-testid="stSidebar"] > div:first-child {{
    background-color: rgba(255, 255, 255, 0.8); /* para que sea legible */
    padding-top: 2rem;
    padding-bottom: 2rem;
    border-radius: 10px;
    margin: 1rem;
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}
</style>
"""

# --- Aplicar estilo ---
st.markdown(page_bg_img, unsafe_allow_html=True)
# --- Diccionario de páginas ---
paginas = {
    "Cuenta / Login": "cuenta.py",
    "Corralones (Precios)": "corralones.py",
    "Panel de Usuario": "panel_de_usuario.py",
    "Registro de Obras": "registro_obra.py",
    "Predictor de Materiales": "predictor.py",
}

# --- Obtener página actual ---
pagina_actual = st.query_params.get("page", "cuenta.py")

# --- Redireccionar automáticamente si no hay sesión ---
if "usuario" not in st.session_state and pagina_actual != "cuenta.py":
    st.query_params["page"] = "cuenta.py"
    st.rerun()

# --- Mostrar navegación solo si está logueado ---
if "usuario" in st.session_state:
    st.sidebar.title("📁 Navegación")
    seleccion = st.sidebar.radio("Elegí una sección:", [k for k in paginas if paginas[k] != "cuenta.py"])
    st.query_params["page"] = paginas[seleccion]
    if paginas[seleccion] != pagina_actual:
        st.rerun()

# --- Cargar y ejecutar el código de la página correspondiente ---
ruta = os.path.join("pages", st.query_params.get("page", "cuenta.py"))
if os.path.exists(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        exec(f.read(), globals())
else:
    st.error("⚠️ No se encontró la página solicitada.")
