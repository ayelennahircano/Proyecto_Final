import streamlit as st
import sqlite3
import qrcode
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# --- URL del formulario y CSV ---
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSePvL6mr9U5R1lfTnzP29w8X6782nrcrDAqcku0nsIktDYAzA/viewform?usp=header"
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTfBC1Q1v4jN3XS2rHZ1VqE8ksLt_J3qY5stWLWffGo85quwITxw4JIq_tCdllYpG1vaXAg6qfDBjvt/pub?gid=1178988507&single=true&output=csv"

# --- Verificar sesión iniciada y expiración ---
if "usuario" not in st.session_state:
    st.warning("⚠️ Debés iniciar sesión para ver el panel.")
    st.stop()

# --- Verificar expiración ---
if time.time() - st.session_state.get("login_time", 0) > 15 * 60:
    st.warning("🔒 Sesión expirada por inactividad.")
    st.session_state.clear()
    st.query_params["page"] = "cuenta.py"
    st.rerun()

usuario = st.session_state["usuario"]

# --- Título y logout ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("CIMIENTO FUTURO")
    st.subheader("Panel del Usuario")
with col2:
    st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.query_params["page"] = "cuenta.py"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Conexión a la base de datos ---
conn = sqlite3.connect("obras.db", check_same_thread=False)

# --- Cargar lista de obras ---
obras = pd.read_sql("SELECT * FROM obras WHERE usuario = ?", conn, params=[usuario])
if obras.empty:
    st.info("No tenés obras registradas todavía.")
    st.stop()

st.subheader("Tus Obras Registradas")
st.dataframe(obras.set_index("nombre_obra"))

# --- Selección de obra ---
st.subheader("Analizar y modificar una obra")
obra_seleccionada = st.selectbox("Elegí una obra:", obras["nombre_obra"].tolist())
obra = obras[obras["nombre_obra"] == obra_seleccionada].iloc[0]

# --- Modificar stock ---
st.markdown("### Modificar stock de materiales")

nombres_materiales = {
    "ladrillo_1": "Ladrillo común 5x12x26",
    "ladrillo_2": "Cerámico portante 19x12x39",
    "ladrillo_3": "Cerámico portante 19x19x33",
    "ladrillo_4": "Cerámico no portante 8x18x33",
    "ladrillo_5": "Cerámico no portante 18x18x33",
    "ladrillo_6": "Bloque de hormigón 19x19x39",
    "cemento": "Cemento (kg)",
    "cal": "Cal (kg)",
    "arena": "Arena (m³)",
    "cemento_alba": "Cemento de albañilería (kg)"
}

nuevos_valores = {}
for col, label in nombres_materiales.items():
    nuevos_valores[col] = st.number_input(label, value=float(obra[col]), step=1.0)

if st.button("Guardar cambios en stock"):
    query = f"""
    UPDATE obras
    SET {', '.join([f"{k} = ?" for k in nuevos_valores.keys()])}
    WHERE nombre_obra = ? AND usuario = ?
    """
    conn.execute(query, list(nuevos_valores.values()) + [obra_seleccionada, usuario])
    conn.commit()
    st.success("✅ Stock actualizado correctamente.")

    # Recargar obra
    obra = pd.read_sql("SELECT * FROM obras WHERE nombre_obra = ? AND usuario = ?", conn, params=[obra_seleccionada, usuario]).iloc[0]

# --- Comparar con materiales estimados ---
try:
    tabla_pred = f"materiales_{obra_seleccionada.strip().replace(' ', '_').lower()}"
    pred = pd.read_sql(f"SELECT * FROM {tabla_pred}", conn)
    pred_totales = pred[["cantidad_ladrillos", "cemento_kg", "cal_kg", "arena_m3", "cemento_albañilería_kg"]].sum()
    st.subheader("Comparación con materiales estimados")
    comparacion = pd.DataFrame({
        "Registrado": [
            obra["ladrillo_5"], obra["cemento"], obra["cal"], obra["arena"], obra["cemento_alba"]
        ],
        "Estimado": [
            pred_totales["cantidad_ladrillos"], pred_totales["cemento_kg"], pred_totales["cal_kg"],
            pred_totales["arena_m3"], pred_totales["cemento_albañilería_kg"]
        ]
    }, index=["Ladrillos", "Cemento", "Cal", "Arena", "Cem. Albañilería"])
    st.dataframe(comparacion)

    fig, ax = plt.subplots()
    comparacion.plot(kind="bar", ax=ax)
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

except Exception as e:
    st.warning("⚠️ No se encontraron materiales estimados para esta obra.")
    st.text(str(e))

# --- Chat y QR en columnas ---
st.subheader("\n\n💬 Comunicación con la obra")
col_chat, col_qr = st.columns([0.65, 0.35])

with col_chat:
    try:
        df_mensajes = pd.read_csv(csv_url)
        columnas = df_mensajes.columns.str.lower()
        if "obra" in columnas:
            col_obra = df_mensajes.columns[columnas == "obra"][0]
            df_mensajes = df_mensajes[df_mensajes[col_obra] == obra_seleccionada]

        nuevos_mensajes = len(df_mensajes)
        if "mensajes_anteriores" not in st.session_state:
            st.session_state["mensajes_anteriores"] = 0

        if nuevos_mensajes > st.session_state["mensajes_anteriores"]:
            st.success(f"¡Hay {nuevos_mensajes - st.session_state['mensajes_anteriores']} mensaje(s) nuevo(s) desde la obra!")
        elif nuevos_mensajes == 0:
            st.info("No hay mensajes todavía.")

        st.session_state["mensajes_anteriores"] = nuevos_mensajes

        if not df_mensajes.empty:
            st.dataframe(df_mensajes)

        st.subheader("Responder mensaje")
        respuesta = st.text_area("Tu respuesta para el equipo")
        if st.button("Enviar respuesta") and respuesta:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales_google.json", scope)
            client = gspread.authorize(creds)

            hoja_admin = None
            sheet = client.open_by_url(csv_url.replace("/pub?", "/edit?")).sheet1
            try:
                hoja_admin = client.open_by_url(csv_url.replace("/pub?", "/edit?")).worksheet("Respuestas_admin")
            except:
                hoja_admin = client.open_by_url(csv_url.replace("/pub?", "/edit?")).add_worksheet("Respuestas_admin", rows="1000", cols="3")
                hoja_admin.append_row(["Usuario", "Obra", "Respuesta"])

            hoja_admin.append_row([usuario, obra_seleccionada, respuesta])
            st.success("✅ Respuesta enviada y registrada en la hoja.")

    except Exception as e:
        st.error("❌ No se pudo cargar el chat desde la hoja de Google.")
        st.text(str(e))

with col_qr:
    st.subheader("Compartir Formulario")
    try:
        qr = qrcode.make(form_url)
        buf = io.BytesIO()
        qr.save(buf)
        st.image(buf.getvalue(), caption="Escaneá este QR", width=250)
        st.write(f"[Abrir formulario]({form_url})")
    except Exception as qr_error:
        st.warning("⚠️ No se pudo generar el QR.")
        st.text(str(qr_error))

