import streamlit as st
import pandas as pd
import joblib
# --- Guardar predicción en la base de datos ---
import sqlite3

# --- Restricción de acceso ---
if 'logueado' not in st.session_state or not st.session_state['logueado']:
    st.error("⚠️ Acceso denegado. Por favor iniciá sesión primero desde la página principal.")
    st.stop()


# --- App principal ---
def app():
    st.title("CIMIENTO FUTURO\n\n")
    st.subheader("Modelo predictivo con IA para cálculo de materiales\n")

    # Cargar modelo y columnas
    modelo_cargado = joblib.load("rf_model.pkl")
    if isinstance(modelo_cargado, tuple) and len(modelo_cargado) == 2:
        modelo, columnas_entrenamiento = modelo_cargado
    else:
        st.error("❌ Error al cargar el modelo. Asegurate de que 'rf_model.pkl' contiene modelo y columnas.")
        st.stop()

    # Variables
    mezclas = ["Cemento + Cal + Arena", "Cemento de Albañilería + Arena"]
    tipos_ladrillo = [
        "Comun 5x12x26",
        "Cerámico portante 19x12x39",
        "Cerámico portante 19x19x33",
        "Ceramico no portante 8x18x33",
        "Ceramico no portante 18x18x33",
        "Bloque hormigon 19x19x39"
    ]
    espesores_por_ladrillo = {
        "Comun 5x12x26": [0.15, 0.30],
        "Cerámico portante 19x12x39": [0.15],
        "Cerámico portante 19x19x33": [0.20],
        "Ceramico no portante 8x18x33": [0.10],
        "Ceramico no portante 18x18x33": [0.20],
        "Bloque hormigon 19x19x39": [0.20],
    }

    parametros_materiales = {
        ("Comun 5x12x26", 0.15, "Cemento + Cal + Arena"): (60, 7.5, 7.3, 0.035, 0),
        ("Comun 5x12x26", 0.15, "Cemento de Albañilería + Arena"): (60, 0, 0, 0.043, 7.7),
        ("Comun 5x12x26", 0.30, "Cemento + Cal + Arena"): (120, 9.9, 19.1, 0.090, 0),
        ("Comun 5x12x26", 0.30, "Cemento de Albañilería + Arena"): (120, 0, 0, 0.115, 15.2),
        ("Cerámico portante 19x12x39", 0.15, "Cemento + Cal + Arena"): (12.5, 0.65, 2.5, 0.012, 0),
        ("Cerámico portante 19x12x39", 0.15, "Cemento de Albañilería + Arena"): (12.5, 0, 0, 0.013, 2.5),
        ("Cerámico portante 19x19x33", 0.20, "Cemento + Cal + Arena"): (12.5, 0.78, 3.0, 0.015, 0),
        ("Cerámico portante 19x19x33", 0.20, "Cemento de Albañilería + Arena"): (12.5, 0, 0, 0.016, 3.0),
        ("Ceramico no portante 8x18x33", 0.10, "Cemento + Cal + Arena"): (15.5, 2.6, 2.5, 0.012, 0),
        ("Ceramico no portante 8x18x33", 0.10, "Cemento de Albañilería + Arena"): (15.5, 0, 0, 0.015, 2.8),
        ("Ceramico no portante 18x18x33", 0.20, "Cemento + Cal + Arena"): (33, 8.5, 7.8, 0.037, 0),
        ("Ceramico no portante 18x18x33", 0.20, "Cemento de Albañilería + Arena"): (33, 0, 0, 0.046, 8.5),
        ("Bloque hormigon 19x19x39", 0.20, "Cemento + Cal + Arena"): (12.5, 3.3, 1.5, 0.015, 0),
        ("Bloque hormigon 19x19x39", 0.20, "Cemento de Albañilería + Arena"): (12.5, 0, 0, 0.013, 4.75),
    }

    # Formulario
    obra = st.text_input("Nombre de la obra")
    tipo_ladrillo = st.selectbox("Tipo de ladrillo", tipos_ladrillo)
    espesor = st.selectbox("Espesor del muro (m)", espesores_por_ladrillo[tipo_ladrillo])
    altura = st.number_input("Altura del muro (m)", min_value=0.5, value=2.5)
    ancho = st.number_input("Ancho del muro (m)", min_value=0.5, value=4.0)
    tipo_mezcla = st.selectbox("Tipo de mezcla", mezclas)
    cantidad = st.number_input("Repetir cuántas veces este muro", min_value=1, value=1)

    if st.button("➕ Agregar muro"):
        area = altura * ancho
        tipo_ladrillo_lower = tipo_ladrillo.lower().strip()
        X_nuevo = pd.DataFrame([{ 
            "Area_muro": area,
            "Altura_muro": altura,
            "Ancho_muro": ancho,
            "Tipo_ladrillo": tipo_ladrillo_lower 
        }])
        X_nuevo = pd.get_dummies(X_nuevo)
        for col in columnas_entrenamiento:
            if col not in X_nuevo.columns:
                X_nuevo[col] = 0
        X_nuevo = X_nuevo[columnas_entrenamiento]
        pred = modelo.predict(X_nuevo)[0] * cantidad

        key = (tipo_ladrillo, espesor, tipo_mezcla)
        if key in parametros_materiales:
            ladrillos_m2, cemento, cal, arena, cemento_alba = parametros_materiales[key]
        else:
            st.error(f"No hay parámetros para {tipo_ladrillo}, {espesor}, {tipo_mezcla}")
            st.stop()

        df_resultado = pd.DataFrame([{
            "ID_obra": obra,
            "Tipo_ladrillo": tipo_ladrillo,
            "Altura_muro": altura,
            "Ancho_muro": ancho,
            "Espesor_muro": espesor,
            "Area_muro": round(area * cantidad, 2),
            "Cantidad_ladrillos": round(pred),
            "Cemento (Kg)": round(cemento * area * cantidad, 2),
            "Cal (Kg)": round(cal * area * cantidad, 2),
            "Arena (m3)": round(arena * area * cantidad, 3),
            "Cemento_albañilería (Kg)": round(cemento_alba * area * cantidad, 2)
        }])

        st.success("✅ Resultados del muro agregado:")
        st.dataframe(df_resultado)

        csv = df_resultado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar resultados", csv, f"materiales_{obra}.csv", "text/csv")

        
        # Conexión a la base de datos
        conn = sqlite3.connect("obras.db", check_same_thread=False)

        # Generar nombre de la tabla: materiales_nombreobra
        tabla_pred = f"materiales_{obra.strip().replace(' ', '_').lower()}"

        # Normalizar nombres de columnas para la tabla
        df_guardar = df_resultado.copy()
        df_guardar.columns = [col.lower().replace(" ", "_").replace("(", "").replace(")", "") for col in df_guardar.columns]

        # Guardar en SQLite
        df_guardar.to_sql(tabla_pred, conn, if_exists="append", index=False)

        st.success("Predicción guardada correctamente en la base de datos.")
        # --- Mostrar todos los muros guardados para la obra actual ---
        st.subheader("📋 Muros acumulados en esta obra")

        try:
            df_acumulado = pd.read_sql(f"SELECT * FROM {tabla_pred}", conn)
            st.dataframe(df_acumulado)

            # --- Botón para descargar todos los muros ---
            csv_total = df_acumulado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar todos los muros", csv_total, f"todos_los_muros_{obra}.csv", "text/csv")
        except Exception as e:
            st.warning("⚠️ No se pudieron mostrar los muros acumulados.")
            st.text(str(e))


# Ejecutar
app()
