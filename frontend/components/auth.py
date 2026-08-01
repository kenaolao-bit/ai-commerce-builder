"""Ecran de connexion admin, partage par toutes les pages Streamlit.

Appelle directement backend.security.auth (pas de requete HTTP) : Streamlit
Community Cloud ne lance qu'un seul processus Python, il n'y a pas de
serveur API separe a joindre.
"""

import streamlit as st

from frontend import services


def require_login() -> None:
    services.ensure_initialized()

    if st.session_state.get("authenticated"):
        with st.sidebar:
            st.caption(f"Connecte : {st.session_state.get('email', '')}")
            if st.button("Se deconnecter"):
                st.session_state.pop("authenticated", None)
                st.session_state.pop("email", None)
                st.rerun()
        return

    st.title("🔒 Connexion administrateur")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    if submitted:
        if services.login(email, password):
            st.session_state["authenticated"] = True
            st.session_state["email"] = email
            st.rerun()
        else:
            st.error("Identifiants invalides.")

    st.stop()
