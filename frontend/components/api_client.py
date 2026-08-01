"""Client HTTP minimal vers le backend FastAPI, partage par toutes les pages Streamlit.

Toutes les routes (hors /auth/login et /health) exigent un token JWT (Principe 11,
section 11 de la specification technique). Le token est stocke dans
st.session_state par frontend.components.auth et attache ici a chaque requete.
"""

import os

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def _url(path: str) -> str:
    return f"{API_BASE_URL.rstrip('/')}{path}"


def _auth_headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def get(path: str, **kwargs):
    response = requests.get(_url(path), headers=_auth_headers(), timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


def post(path: str, json: dict | None = None, **kwargs):
    response = requests.post(
        _url(path), json=json or {}, headers=_auth_headers(), timeout=30, **kwargs
    )
    response.raise_for_status()
    return response.json()
