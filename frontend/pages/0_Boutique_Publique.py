"""Boutique publique cliente (MVP lancement Togo).

NOTE: cette page vit dans frontend/pages/ (comme les pages admin) afin de
partager EXACTEMENT la meme base de donnees SQLite que le panneau admin :
sur Streamlit Community Cloud, chaque app deployee separement a sa propre
base isolee ; une boutique deployee comme app distincte ne verrait jamais
les memes donnees et l'administrateur ne verrait jamais les commandes des
clients. En restant une page de la MEME app, tout reste synchronise.

Contrairement a frontend/app.py (tableau de bord prive de l'administrateur),
ce fichier est la page que les CLIENTS voient et utilisent pour commander.
Aucune connexion requise. Reutilise directement frontend.services (memes
fonctions backend que le panneau admin) pour rester coherent avec les
donnees deja generees (marque, produits, boutique).

MVP : une seule campagne active (CAMPAIGN_ID = 1). A adapter si plusieurs
boutiques sont lancees en parallele.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from frontend import services

CAMPAIGN_ID = 1

# --- Coordonnees Mobile Money / contact (Lao KENAO) ---
NUMERO_YAS_TMONEY = "+228 71 45 45 40"
NUMERO_MOOV_MONEY = "+228 97 97 11 11"
CONTACT_WHATSAPP = "+228 97 97 11 11"
# -------------------------------------------------------

st.set_page_config(page_title="Boutique en ligne", page_icon="🛍️", layout="wide")

services.ensure_initialized()

brand = services.get_brand(CAMPAIGN_ID)
store = services.get_store(CAMPAIGN_ID)

if not brand or not store:
    st.title("Boutique en cours de preparation")
    st.info("Revenez tres bientot !")
    st.stop()

palette = brand.get("palette_couleurs", {}) or {}
couleur_primaire = palette.get("primaire", "#1B4332")

st.markdown(
    f"<h1 style='color:{couleur_primaire}; margin-bottom:0;'>{brand['nom']}</h1>",
    unsafe_allow_html=True,
)
st.caption(brand["slogan"])
st.divider()

produits = [p for p in services.list_products(CAMPAIGN_ID) if p["statut"] == "importe"]

if not produits:
    st.info("Aucun produit disponible pour le moment. Revenez bientot !")
    st.stop()

st.subheader("Nos produits")

cols = st.columns(3)
for i, p in enumerate(produits):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{p['nom']}**")
            st.markdown(f"### {p['prix_conseille']:,.0f} XOF".replace(",", " "))

st.divider()
st.subheader("Passer une commande")

noms_produits = [f"{p['nom']} — {p['prix_conseille']:,.0f} XOF".replace(",", " ") for p in produits]
choix = st.selectbox("Produit souhaite", noms_produits)
produit_choisi = produits[noms_produits.index(choix)]

with st.form("commande_client"):
    nom_client = st.text_input("Votre nom complet")
    contact_client = st.text_input("Votre numero de telephone")
    quantite = st.number_input("Quantite", min_value=1, value=1, step=1)
    valider = st.form_submit_button("Valider ma commande")

if valider:
    if not nom_client.strip() or not contact_client.strip():
        st.error("Merci de renseigner votre nom et votre numero de telephone.")
    else:
        montant_total = produit_choisi["prix_conseille"] * quantite
        montant_affiche = f"{montant_total:,.0f}".replace(",", " ")
        try:
            commande = services.create_order(
                store_id=store["id"],
                client_nom=nom_client.strip(),
                client_contact=contact_client.strip(),
                montant=montant_total,
            )
            st.success(f"Commande #{commande['id']} enregistree ! Merci {nom_client.strip()}.")
            st.markdown(
                f"""
**Pour finaliser votre commande :**

1. Envoyez **{montant_affiche} XOF** via l'un de ces moyens :
   - **YAS TMoney** : {NUMERO_YAS_TMONEY}
   - **Moov Money** : {NUMERO_MOOV_MONEY}
2. Envoyez-nous la reference de votre transaction par **WhatsApp** au
   **{CONTACT_WHATSAPP}**, en mentionnant le numero de commande **#{commande['id']}**
3. Votre commande sera confirmee et traitee dans les plus brefs delais.

Merci de votre confiance !
"""
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Impossible d'enregistrer la commande : {exc}")
