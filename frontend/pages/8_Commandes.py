import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import streamlit as st

from frontend import services
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Commandes", page_icon="🛒", layout="wide")
require_login()
st.title("🛒 Commandes")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"], "Executer l'etape 'Preparation des ventes'")

store = services.get_store(campaign["id"])
if store is None:
    st.info("Boutique non encore initialisee.")
    st.stop()

store_id = store["id"]

st.subheader("Nouvelle commande")
with st.form("nouvelle_commande"):
    client_nom = st.text_input("Nom du client")
    client_contact = st.text_input("Contact du client (telephone/email)")
    montant = st.number_input("Montant (XOF)", min_value=0.0, value=5000.0, step=500.0)
    submitted = st.form_submit_button("Creer la commande")

if submitted:
    order = services.create_order(
        store_id=store_id, client_nom=client_nom, client_contact=client_contact, montant=montant
    )
    st.success(f"Commande #{order['id']} creee.")
    st.rerun()

st.divider()
st.subheader("Initier un paiement")
providers = services.list_payment_providers()
order_id_input = st.number_input("ID de la commande", min_value=1, step=1)
provider_choisi = st.selectbox("Moyen de paiement", providers)
if st.button("Initier le paiement"):
    try:
        result = services.initiate_payment(
            order_id=int(order_id_input), provider=provider_choisi, currency="XOF"
        )
        st.success(result["message"] or "Paiement initie.")
        if result["instructions"]:
            st.info(result["instructions"].get("message", ""))
        st.json(result["payment"])
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur : {exc}")

st.divider()
st.subheader("Confirmer un paiement manuel (action administrateur)")
tx_ref = st.text_input("Reference de transaction (paiement manuel)")
action_col1, action_col2 = st.columns(2)
if action_col1.button("Confirmer le paiement") and tx_ref:
    try:
        services.confirm_manual_payment(tx_ref, "confirm")
        st.success("Paiement confirme.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur : {exc}")
if action_col2.button("Rejeter le paiement") and tx_ref:
    try:
        services.confirm_manual_payment(tx_ref, "reject")
        st.warning("Paiement rejete.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Erreur : {exc}")
