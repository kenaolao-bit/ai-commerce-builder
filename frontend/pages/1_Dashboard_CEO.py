import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import streamlit as st

from frontend import services
from frontend.components.auth import require_login

st.set_page_config(page_title="Dashboard CEO", page_icon="📊", layout="wide")
require_login()
st.title("📊 Dashboard CEO")

if st.button("Rafraichir"):
    st.rerun()

try:
    kpis = services.get_dashboard_kpis()
except Exception as exc:  # noqa: BLE001
    st.error(f"Impossible de charger les indicateurs : {exc}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires", f"{kpis['chiffre_affaires_total']:,.0f} XOF")
col2.metric("Ventes", kpis["nombre_ventes"])
col3.metric("Commandes", kpis["nombre_commandes"])
col4.metric("Produits actifs", kpis["produits_actifs"])

st.subheader("Progression des campagnes")
if kpis["campagnes"]:
    for c in kpis["campagnes"]:
        st.write(f"**{c['nom']}** (#{c['id']}) — {c['statut']}")
        st.progress(c["etape_courante"] / c["total_etapes"])
        st.caption(f"Etape {c['etape_courante']}/{c['total_etapes']}")
else:
    st.info("Aucune campagne en cours.")

st.subheader("Alertes")
if kpis["alertes"]:
    for alerte in kpis["alertes"]:
        st.warning(alerte)
else:
    st.success("Aucune alerte.")
