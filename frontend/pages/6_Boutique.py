import streamlit as st

from frontend.components.api_client import get
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Boutique", page_icon="🏬", layout="wide")
require_login()
st.title("🏬 Boutique")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"])

try:
    store = get(f"/campaigns/{campaign['id']}/store")
except Exception:
    st.info("Boutique non encore initialisee. Executez l'etape ci-dessus.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Statut", store["statut"])
col2.metric("Score qualite", f"{store['score_qualite']:.0f}/100")

try:
    quality = get(f"/campaigns/{campaign['id']}/store/quality")
    with st.expander("Checklist qualite"):
        for c in quality["checklist"]:
            icone = "✅" if c["ok"] else "❌"
            st.write(f"{icone} {c['critere']} — {c['detail']}")
except Exception:
    pass

st.subheader("Pages generees")
for page in store.get("pages", []):
    with st.expander(page["type"].capitalize()):
        st.text(page["contenu"])
