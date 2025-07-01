import streamlit as st
import sqlite3

# --- Verificar sesión ---
if "usuario" not in st.session_state:
    st.warning("⚠️ Debés iniciar sesión para continuar.")
    st.stop()

# --- Verificar expiración ---
import time
if time.time() - st.session_state.get("login_time", 0) > 15 * 60:
    st.warning("🔒 Sesión expirada por inactividad.")
    st.session_state.clear()
    st.query_params["page"] = "cuenta.py"
    st.rerun()

# --- Conexión a base de datos ---
conn = sqlite3.connect("obras.db", check_same_thread=False)
c = conn.cursor()

# --- Formulario de obra ---
def mostrar_formulario_obra():
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("CIMIENTO FUTURO")
        st.subheader("Registro de Obra")
    with col2:
        st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar sesión"):
            st.session_state.clear()
            st.query_params["page"] = "cuenta.py"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    nombre_obra = st.text_input("🪧 Nombre de la obra")

    nombres_ladrillos = [
        "Cerámico portante 19x19x33",
        "Cerámico portante 19x12x39",
        "Cerámico no portante 18x18x33",
        "Cerámico no portante 8x18x33",
        "Bloque de hormigón 19x19x39",
        "Ladrillo común 5x12x26"
    ]

    materiales = {}
    for i, nombre in enumerate(nombres_ladrillos, start=1):
        materiales[f"ladrillo_{i}"] = st.number_input(f"{nombre} (unidades)", min_value=0)

    cal = st.number_input("Cal (kg)", min_value=0.0)
    cemento = st.number_input("Cemento (kg)", min_value=0.0)
    cemento_alba = st.number_input("Cemento Albañilería (kg)", min_value=0.0)
    arena = st.number_input("Arena (m3)", min_value=0.0)

    if st.button("✅ Registrar obra"):
        if not nombre_obra:
            st.error("⚠️ El nombre de la obra no puede estar vacío.")
            return

        try:
            c.execute('''
                CREATE TABLE IF NOT EXISTS obras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    nombre_obra TEXT UNIQUE,
                    ladrillo_1 INTEGER,
                    ladrillo_2 INTEGER,
                    ladrillo_3 INTEGER,
                    ladrillo_4 INTEGER,
                    ladrillo_5 INTEGER,
                    ladrillo_6 INTEGER,
                    cal REAL,
                    cemento REAL,
                    cemento_alba REAL,
                    arena REAL
                )
            ''')

            c.execute('''
                INSERT INTO obras (
                    usuario, nombre_obra, ladrillo_1, ladrillo_2, ladrillo_3,
                    ladrillo_4, ladrillo_5, ladrillo_6, cal, cemento, cemento_alba, arena
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                st.session_state["usuario"], nombre_obra,
                materiales["ladrillo_1"], materiales["ladrillo_2"], materiales["ladrillo_3"],
                materiales["ladrillo_4"], materiales["ladrillo_5"], materiales["ladrillo_6"],
                cal, cemento, cemento_alba, arena
            ))

            conn.commit()
            st.success(f"✅ Obra '{nombre_obra}' registrada correctamente para el usuario {st.session_state['usuario']}.")

        except sqlite3.IntegrityError:
            st.error("❌ Ya existe una obra registrada con ese nombre. Elegí otro.")

# Ejecutar formulario
mostrar_formulario_obra()
