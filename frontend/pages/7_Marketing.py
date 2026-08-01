import streamlit as st

from frontend import services
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Marketing", page_icon="📣", layout="wide")
require_login()
st.title("📣 Marketing")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"], "Executer l'etape 'Preparation du marketing'")

assets = services.list_marketing_assets(campaign["id"])
if not assets:
    st.info("Aucun contenu marketing pour le moment. Executez l'etape ci-dessus.")
    st.stop()

for asset in assets:
    with st.expander(f"{asset['type'].capitalize()} — {asset['statut']}"):
        st.text(asset["contenu"])
