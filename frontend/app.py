"""Point d'entree Streamlit (030_Technical_Specification, section 3)."""

import streamlit as st

from frontend.components.auth import require_login

st.set_page_config(page_title="AI Commerce Builder", page_icon="🛒", layout="wide")
require_login()

st.title("AI Commerce Builder")
st.caption("Moteur IA prive pour automatiser le lancement d'une activite e-commerce.")

st.markdown(
    """
Utilisez le menu lateral pour naviguer dans le flux metier :

1. **Dashboard CEO** — indicateurs globaux
2. **Nouvelle Campagne** — creer une campagne
3. **Niches** — recherche et selection de niche
4. **Produits** — recherche et import de produits
5. **Marque** — identite de marque generee
6. **Boutique** — pages generees et score qualite
7. **Marketing** — contenus generes
8. **Commandes** — commandes et paiements
"""
)
