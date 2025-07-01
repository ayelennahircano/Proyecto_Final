import streamlit as st
import base64
import os
import time

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Cimiento Futuro", layout="wide")

# --- FUNCIONES ---

@st.cache_data
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- APLICAR FONDO GLOBAL ---
if os.path.exists("background.png"):
    img_base64 = get_img_as_base64("background.png")

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
        background-color: rgba(255, 255, 255, 0.85);
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
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- SESIÓN Y EXPIRACIÓN ---
if "usuario" in st.session_state:
    if time.time() - st.session_state.get("login_time", 0) > 15 * 60:
        st.warning("🔒 Tu sesión expiró por inactividad.")
        st.session_state.clear()
        st.rerun()

# --- TÍTULO Y MENSAJE BIENVENIDA ---
st.title("Cimiento Futuro\n\n")
st.subheader("Sistema de gestión de obras con IA y análisis de materiales\n")

# --- MENÚ DE ACCESO RÁPIDO ---
st.markdown("""
### Accedé a los módulos disponibles:
- **Registro de obra**  
- **Predictor de materiales con IA**  
- **Panel de usuario**
- **Comparador de precios de corralones**

Usá el menú lateral o el menú superior para acceder a cada uno.
""")

# --- SESIÓN INICIADA ---
if "usuario" in st.session_state:
    st.success(f"🔐 Sesión iniciada como: {st.session_state['usuario']}")
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
else:
    st.info("🟡 Iniciá sesión desde la página `cuenta.py` para acceder a todas las funciones.")
