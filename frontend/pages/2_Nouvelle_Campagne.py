import streamlit as st

from frontend import services
from frontend.components.auth import require_login

st.set_page_config(page_title="Nouvelle Campagne", page_icon="🚀", layout="wide")
require_login()
st.title("🚀 Nouvelle Campagne")

with st.form("nouvelle_campagne"):
    nom = st.text_input("Nom de la campagne", value="Ma boutique")
    pays_cible = st.text_input("Pays cible", value="Togo")
    langue = st.text_input("Langue", value="fr")
    budget = st.number_input("Budget (XOF)", min_value=0.0, value=200000.0, step=10000.0)
    objectif = st.text_area("Objectif", value="Vendre des produits rentables en ligne")
    submitted = st.form_submit_button("Creer la campagne")

if submitted:
    try:
        campaign = services.create_campaign(
            nom=nom, pays_cible=pays_cible, langue=langue, budget=budget, objectif=objectif
        )
        st.success(f"Campagne #{campaign['id']} creee : {campaign['nom']}")
        st.json(campaign)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur lors de la creation de la campagne : {exc}")

st.divider()
st.subheader("Campagnes existantes")
try:
    campaigns = services.list_campaigns()
    if campaigns:
        st.dataframe(campaigns, use_container_width=True)
    else:
        st.info("Aucune campagne pour le moment.")
except Exception as exc:  # noqa: BLE001
    st.error(f"Impossible de charger les campagnes : {exc}")
