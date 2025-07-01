import streamlit as st
import sqlite3
import time

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

# --- Logout y expiración ---
def logout():
    st.session_state.clear()
    st.query_params["page"] = "cuenta.py"
    st.rerun()

def verificar_sesion():
    if st.session_state.get("logueado"):
        tiempo_limite = 15 * 60  # 15 minutos
        if time.time() - st.session_state.get("login_time", 0) > tiempo_limite:
            st.warning("🔒 Sesión expirada por inactividad.")
            logout()

# --- Interfaz principal ---
def app():
    crear_tabla_usuarios()
    verificar_sesion()

    st.title("CIMIENTO FUTURO")
    st.markdown("""
Cimiento Futuro es una solución innovadora para la construcción basada en IA y ciencia de datos. Registrate para llevar control predictivo de tu obra.
""")

    # --- Si ya hay sesión activa ---
    if st.session_state.get("logueado"):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.success(f"✅ Logueado como: {st.session_state['usuario']}")
        with col2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            if st.button("🚪 Cerrar sesión"):
                logout()
            st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- Formulario login / registro ---
    choice = st.selectbox('Login / Registro', ['Ingresar', 'Registrarse'])

    if choice == 'Ingresar':
        email = st.text_input('Correo electrónico')
        password = st.text_input('Contraseña', type='password')
        if st.button('Ingresar'):
            usuario = verificar_usuario(email, password)
            if usuario:
                st.success(f"Bienvenido/a {usuario[2]}")
                st.session_state['usuario'] = usuario[2]
                st.session_state['logueado'] = True
                st.session_state['login_time'] = time.time()
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

# --- Ejecutar ---
app()
