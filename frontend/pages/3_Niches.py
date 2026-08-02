import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import streamlit as st

from frontend import services
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Niches", page_icon="🧭", layout="wide")
require_login()
st.title("🧭 Niches")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"], "Executer l'etape 'Recherche de niche'")

st.subheader("Niches proposees")
niches = services.list_niches(campaign["id"])
if not niches:
    st.info("Aucune niche pour le moment. Executez l'etape 1 ci-dessus.")
    st.stop()

st.dataframe(niches, use_container_width=True)

st.subheader("Selectionner la niche retenue")
options = {f"#{n['id']} - {n['nom']} (score {n['score_opportunite']})": n["id"] for n in niches}
choix = st.selectbox("Niche", list(options.keys()))
if st.button("Retenir cette niche"):
    try:
        niche = services.select_niche(campaign["id"], options[choix])
        st.success(f"Niche retenue : {niche['nom']}")
        st.rerun()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur : {exc}")
