import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import streamlit as st

from frontend import services
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Boutique", page_icon="🏬", layout="wide")
require_login()
st.title("🏬 Boutique")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"])

store = services.get_store(campaign["id"])
if store is None:
    st.info("Boutique non encore initialisee. Executez l'etape ci-dessus.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Statut", store["statut"])
col2.metric("Score qualite", f"{store['score_qualite']:.0f}/100")

quality = services.get_store_quality(campaign["id"])
if quality is not None:
    with st.expander("Checklist qualite"):
        for c in quality["checklist"]:
            icone = "✅" if c["ok"] else "❌"
            st.write(f"{icone} {c['critere']} — {c['detail']}")

st.subheader("Pages generees")
for page in store.get("pages", []):
    with st.expander(page["type"].capitalize()):
        st.text(page["contenu"])
