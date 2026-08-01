"""Store Builder (030_Technical_Specification, section 7).

Genere les pages store_pages (accueil, catalogue, fiche produit, FAQ, contact,
politiques, panier) a partir de templates parametres par la marque et les
produits de la campagne. MVP jour J : rendu Streamlit multi-pages consultable
en interne, pas de boutique publique separee.
"""

from sqlalchemy.orm import Session

from backend.models.campaign import Campaign
from backend.models.store import Store, StorePage

PAGE_TYPES = ["accueil", "catalogue", "produit", "faq", "contact", "politiques", "panier"]

DEFAULT_TEMPLATES = {
    "accueil": "Bienvenue sur {nom_boutique}. Boutique en cours de construction.",
    "catalogue": "Le catalogue de {nom_boutique} sera affiche ici des l'import des produits.",
    "produit": "Les fiches produits de {nom_boutique} seront generees a l'import des produits.",
    "faq": (
        "FAQ - {nom_boutique}\n\n"
        "Q: Quels moyens de paiement acceptez-vous ?\n"
        "R: Mobile Money (YAS TMoney, Moov Money), carte bancaire, et paiement manuel.\n\n"
        "Q: Livrez-vous au Togo ?\n"
        "R: Oui, la livraison est disponible sur tout le territoire."
    ),
    "contact": "Contactez {nom_boutique} par email ou telephone (a completer par l'administrateur).",
    "politiques": (
        "Politique de retour, de livraison et de confidentialite de {nom_boutique}. "
        "Document a completer selon la reglementation en vigueur."
    ),
    "panier": "Votre panier chez {nom_boutique} est actuellement vide.",
}


def init_store(db: Session, campaign: Campaign) -> Store:
    store = db.query(Store).filter(Store.campaign_id == campaign.id).first()
    if store is None:
        store = Store(
            campaign_id=campaign.id,
            nom_boutique=campaign.nom,
            url="",
            statut="brouillon",
            score_qualite=0.0,
        )
        db.add(store)
        db.flush()

    pages_existantes = {p.type for p in db.query(StorePage).filter(StorePage.store_id == store.id)}
    for type_page in PAGE_TYPES:
        if type_page not in pages_existantes:
            contenu = DEFAULT_TEMPLATES[type_page].format(nom_boutique=store.nom_boutique)
            db.add(StorePage(store_id=store.id, type=type_page, contenu=contenu))
    db.flush()
    return store


def _catalogue_contenu(nom_boutique: str, produits: list) -> str:
    lignes = [f"Catalogue - {nom_boutique}", ""]
    for p in produits:
        lignes.append(f"- {p.nom} : {p.prix_conseille:,.0f} XOF")
    return "\n".join(lignes) if produits else f"Catalogue - {nom_boutique}\n\nAucun produit importe."


def _produit_contenu(nom_boutique: str, produits: list) -> str:
    blocs = [f"Fiches produits - {nom_boutique}", ""]
    for p in produits:
        blocs.append(
            f"### {p.nom}\nPrix : {p.prix_conseille:,.0f} XOF\n"
            f"Fournisseur : {p.fournisseur}\nMarge estimee : {p.marge_estimee:,.0f} XOF\n"
        )
    return "\n".join(blocs) if produits else f"Fiches produits - {nom_boutique}\n\nAucun produit importe."


def _accueil_contenu(brand, nom_boutique: str) -> str:
    if brand is None:
        return f"Bienvenue sur {nom_boutique}."
    return f"Bienvenue sur {brand.nom}\n{brand.slogan}\n\nPalette : {brand.palette_couleurs}"


def inject_products_and_brand(db: Session, store: Store, brand, produits: list) -> Store:
    if store is None:
        raise ValueError("Store introuvable : BOUTIQUE_INIT doit s'executer avant PRODUITS_IMPORT.")

    nom_boutique = brand.nom if brand is not None else store.nom_boutique
    store.nom_boutique = nom_boutique

    contenus = {
        "accueil": _accueil_contenu(brand, nom_boutique),
        "catalogue": _catalogue_contenu(nom_boutique, produits),
        "produit": _produit_contenu(nom_boutique, produits),
    }

    pages = {p.type: p for p in db.query(StorePage).filter(StorePage.store_id == store.id)}
    for type_page, contenu in contenus.items():
        page = pages.get(type_page)
        if page is not None:
            page.contenu = contenu

    db.flush()
    return store
