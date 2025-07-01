import streamlit as st
import os

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
