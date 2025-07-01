import streamlit as st
import sqlite3
from hashlib import sha256

# --- Funciones de base de datos ---
def crear_tabla_usuarios():
    conn = sqlite3.connect("obras.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def agregar_usuario(email, username, password):
    conn = sqlite3.connect("obras.db")
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (email, username, password) VALUES (?, ?, ?)", (email, username, password))
    conn.commit()
    conn.close()

def verificar_usuario(email, password):
    conn = sqlite3.connect("obras.db")
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email, password))
    usuario = c.fetchone()
    conn.close()
    return usuario

# --- Interfaz principal ---
def app():
    crear_tabla_usuarios()
    st.title("CIMIENTO FUTURO")
    st.markdown("""
Cimiento Futuro es una solución innovadora para la construcción basada en IA y ciencia de datos. Registrate para llevar control predictivo de tu obra.
""")

    choice = st.selectbox('Login / Registro', ['Ingresar', 'Registrarse'])

    if choice == 'Ingresar':
        email = st.text_input('Correo electrónico')
        password = st.text_input('Contraseña', type='password')
        if st.button('Ingresar'):
            usuario = verificar_usuario(email, password)
            if usuario:
                st.success(f"Bienvenido/a {usuario[2]}")
                st.session_state['usuario'] = usuario[2]  # username
                st.session_state['logueado'] = True
                st.query_params["page"] = "corralones"
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

    else:
        email = st.text_input('Correo electrónico')
        username = st.text_input('Nombre de usuario')
        password = st.text_input('Contraseña', type='password')
        if st.button('Registrarse'):
            try:
                agregar_usuario(email, username, password)
                st.success("✅ Usuario registrado correctamente")
            except sqlite3.IntegrityError:
                st.error("⚠️ Ya existe un usuario con ese correo")

app()
