"""Selecteur de campagne partage entre les pages Streamlit du flux metier."""

import streamlit as st

from frontend.components.api_client import get, post


def select_campaign() -> dict | None:
    campaigns = get("/campaigns")
    if not campaigns:
        st.info("Aucune campagne. Creez-en une depuis la page 'Nouvelle Campagne'.")
        return None

    options = {f"#{c['id']} - {c['nom']} (etape {c['etape_courante']}/8)": c for c in campaigns}
    label = st.selectbox("Campagne", list(options.keys()))
    return options[label]


def advance_button(campaign_id: int, label: str = "Executer l'etape suivante") -> None:
    if st.button(label):
        try:
            result = post(f"/campaigns/{campaign_id}/advance")
            label_etape = result["resultat"].get("label", "")
            st.success(f"Etape {result['etape_executee']}/8 executee : {label_etape}")
            st.json(result["resultat"])
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Erreur lors de l'execution de l'etape : {exc}")
