"""Ecran de connexion admin, partage par toutes les pages Streamlit."""

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def require_login() -> None:
    if st.session_state.get("token"):
        with st.sidebar:
            st.caption(f"Connecte : {st.session_state.get('email', '')}")
            if st.button("Se deconnecter"):
                st.session_state.pop("token", None)
                st.session_state.pop("email", None)
                st.rerun()
        return

    st.title("🔒 Connexion administrateur")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    if submitted:
        try:
            response = requests.post(
                f"{API_BASE_URL.rstrip('/')}/auth/login",
                json={"email": email, "password": password},
                timeout=30,
            )
            response.raise_for_status()
            st.session_state["token"] = response.json()["access_token"]
            st.session_state["email"] = email
            st.rerun()
        except Exception:  # noqa: BLE001
            st.error("Identifiants invalides.")

    st.stop()
