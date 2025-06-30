import streamlit as st
import os

# --- Simular ruta de pages ---
pages_dir = "pages"

# --- Diccionario de páginas ---
paginas = {
    "Cuenta / Login": "cuenta.py",
    "Corralones (Precios)": "corralones.py",
    "Panel de Usuario": "panel_de_usuario.py",
    "Registro de Obras": "registro_obra.py",
    "Predictor de Materiales": "predictor.py",
}

# --- Obtener página actual desde query_params ---
pagina_actual = st.query_params.get("page", "cuenta.py")

# --- Título ---
st.markdown("# CIMIENTO FUTURO")

# --- Mostrar navegación si está logueado ---
if "usuario" in st.session_state:
    st.markdown("### Navegación")

    # Lista de opciones sin la página de login
    opciones = [nombre for nombre, archivo in paginas.items() if archivo != "cuenta.py"]
    seleccion = st.radio("Ir a:", opciones, horizontal=True)

    # Cambiar de página según selección
    st.query_params["page"] = paginas[seleccion]
    if paginas[seleccion] != pagina_actual:
        st.rerun()

else:
    # Si no hay sesión activa, forzar a cuenta.py
    if pagina_actual != "cuenta.py":
        st.query_params["page"] = "cuenta.py"
        st.rerun()

# --- Cargar contenido de la página seleccionada ---
ruta_pagina = os.path.join(pages_dir, pagina_actual)
if os.path.exists(ruta_pagina):
    with open(ruta_pagina, "r", encoding="utf-8") as f:
        codigo = f.read()
    exec(codigo, globals())
else:
    st.error(f"⚠️ No se encontró la página {pagina_actual}")
