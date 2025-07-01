import streamlit as st
import sqlite3

# --- Verificar sesión ---
if 'logueado' not in st.session_state or not st.session_state['logueado']:
    st.error("⚠️ Acceso denegado. Por favor iniciá sesión primero desde la página principal.")
    st.stop()

# --- Conexión a base de datos ---
conn = sqlite3.connect("obras.db", check_same_thread=False)
c = conn.cursor()

# --- Formulario de obra ---
def mostrar_formulario_obra():
    st.title("CIMIENTO FUTURO\n\n")
    st.subheader("Registro de Obra\n")

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

    st.write("DEBUG usuario actual:", st.session_state.get("usuario"))
    if st.button("✅ Registrar obra"):
        cursor = conn.cursor()
        cursor.execute('''
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


        cursor.execute('''
            INSERT INTO obras (usuario, nombre_obra, ladrillo_1, ladrillo_2, ladrillo_3,
            ladrillo_4, ladrillo_5, ladrillo_6, cal, cemento, cemento_alba, arena)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state["usuario"], nombre_obra,
            materiales["ladrillo_1"], materiales["ladrillo_2"], materiales["ladrillo_3"],
            materiales["ladrillo_4"], materiales["ladrillo_5"], materiales["ladrillo_6"],
            cal, cemento, cemento_alba, arena
        ))


        conn.commit()
        st.success(f"✅ Obra registrada correctamente para el usuario {st.session_state['usuario']}.")

# Ejecutar formulario
mostrar_formulario_obra()
