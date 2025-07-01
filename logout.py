# logout.py

import streamlit as st
import time

def logout():
    st.session_state.clear()
    st.query_params["page"] = "cuenta.py"
    st.rerun()

def verificar_sesion(tiempo_limite=15*60):
    if st.session_state.get("logueado"):
        if time.time() - st.session_state.get("login_time", 0) > tiempo_limite:
            st.warning("🔒 Sesión expirada por inactividad.")
            logout()

def mostrar_logout():
    if st.session_state.get("logueado"):
        col1, col2 = st.columns([0.7, 0.3])
        with col2:
            with st.container():
                st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                if st.button("🚪 Cerrar sesión"):
                    logout()
                st.markdown("</div>", unsafe_allow_html=True)
