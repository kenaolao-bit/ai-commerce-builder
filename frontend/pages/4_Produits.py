import streamlit as st

from frontend.components.api_client import get, post
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Produits", page_icon="📦", layout="wide")
require_login()
st.title("📦 Produits")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"], "Executer l'etape 'Recherche de produits'")

st.subheader("Produits proposes")
produits = get(f"/campaigns/{campaign['id']}/products")
if not produits:
    st.info("Aucun produit pour le moment. Executez l'etape ci-dessus (apres avoir choisi une niche).")
    st.stop()

st.dataframe(produits, use_container_width=True)

proposes = [p for p in produits if p["statut"] == "propose"]
if proposes:
    st.subheader("Importer des produits")
    options = {f"#{p['id']} - {p['nom']}": p["id"] for p in proposes}
    choix = st.multiselect("Produits a importer", list(options.keys()))
    if st.button("Importer la selection") and choix:
        try:
            post(
                f"/campaigns/{campaign['id']}/products/import",
                json={"product_ids": [options[c] for c in choix]},
            )
            st.success("Produits importes.")
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Erreur : {exc}")
