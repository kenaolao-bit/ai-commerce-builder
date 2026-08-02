import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import streamlit as st

from frontend import services
from frontend.components.auth import require_login
from frontend.components.campaign_selector import advance_button, select_campaign

st.set_page_config(page_title="Marque", page_icon="🎨", layout="wide")
require_login()
st.title("🎨 Marque")

campaign = select_campaign()
if campaign is None:
    st.stop()

advance_button(campaign["id"], "Executer l'etape 'Creation de la marque'")

brand = services.get_brand(campaign["id"])
if brand is None:
    st.info("Marque non encore creee. Executez l'etape ci-dessus.")
    st.stop()

st.subheader(brand["nom"])
st.write(brand["slogan"])

palette = brand.get("palette_couleurs", {})
if palette:
    cols = st.columns(len(palette))
    for col, (nom_couleur, hex_code) in zip(cols, palette.items()):
        with col:
            st.color_picker(nom_couleur, value=hex_code, disabled=True)

if brand.get("logo_placeholder_url"):
    st.image(brand["logo_placeholder_url"], caption="Logo placeholder (MVP)", width=200)
