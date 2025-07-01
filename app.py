import streamlit as st
import base64
import os
import time

# Configuración de la página
st.set_page_config(page_title="Cimiento Futuro", layout="wide")

# --- FONDO GLOBAL ---
def set_background_from_local(png_file):
    with open(png_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    section.main {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    div[data-testid="stSidebarContent"] {{
        background-color: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 1rem;
    }}

    header[data-testid="stHeader"] {{
        background: transparent;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Aplicar fondo si existe ---
if os.path.exists("background.png"):
    set_background_from_local("background.png")

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
