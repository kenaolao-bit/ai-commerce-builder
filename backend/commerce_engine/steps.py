"""Definition des 8 etapes pilotees par le Commerce Engine (030_Technical_Specification, section 5).

Chaque etape :
- lit l'etat de la campagne en base ;
- execute le module IA (ou Store Builder / Payment Engine) correspondant ;
- ecrit le resultat en base ;
- retourne un resume expose a l'appelant (endpoint /campaigns/{id}/advance) et au Dashboard CEO.
"""

from enum import IntEnum

from sqlalchemy.orm import Session

from backend.ai_engine.brand_builder import build_brand
from backend.ai_engine.marketing_generator import generate_marketing
from backend.ai_engine.niche_finder import find_niches
from backend.ai_engine.product_finder import find_products
from backend.ai_engine.quality_checker import check_quality
from backend.models.brand import Brand
from backend.models.campaign import Campaign
from backend.models.marketing import MarketingAsset
from backend.models.niche import Niche
from backend.models.product import Product
from backend.store_builder.builder import init_store, inject_products_and_brand


class CampaignStep(IntEnum):
    NICHE_RECHERCHE = 1
    BOUTIQUE_INIT = 2
    PRODUITS_RECHERCHE = 3
    MARQUE_CREATION = 4
    BOUTIQUE_VERIFICATION = 5
    PRODUITS_IMPORT = 6
    MARKETING_PREPARATION = 7
    VENTES_PREPARATION = 8


STEP_LABELS: dict[int, str] = {
    CampaignStep.NICHE_RECHERCHE: "Recherche de niche",
    CampaignStep.BOUTIQUE_INIT: "Initialisation de la boutique",
    CampaignStep.PRODUITS_RECHERCHE: "Recherche de produits",
    CampaignStep.MARQUE_CREATION: "Creation de la marque",
    CampaignStep.BOUTIQUE_VERIFICATION: "Verification de la boutique",
    CampaignStep.PRODUITS_IMPORT: "Import des produits",
    CampaignStep.MARKETING_PREPARATION: "Preparation du marketing",
    CampaignStep.VENTES_PREPARATION: "Preparation des ventes",
}


def step_niche_recherche(db: Session, campaign: Campaign) -> dict:
    niches_proposees = find_niches(
        pays_cible=campaign.pays_cible,
        langue=campaign.langue,
        budget=campaign.budget,
        objectif=campaign.objectif,
    )
    for n in niches_proposees:
        db.add(
            Niche(
                campaign_id=campaign.id,
                nom=n["nom"],
                score_opportunite=n["score_opportunite"],
                niveau_concurrence=n["niveau_concurrence"],
                recommandation=n["recommandation"],
                statut="proposee",
            )
        )
    db.flush()
    return {"niches_proposees": len(niches_proposees)}


def step_boutique_init(db: Session, campaign: Campaign) -> dict:
    store = init_store(db, campaign)
    return {"store_id": store.id, "statut": store.statut}


def step_produits_recherche(db: Session, campaign: Campaign) -> dict:
    niche_retenue = (
        db.query(Niche)
        .filter(Niche.campaign_id == campaign.id, Niche.statut == "retenue")
        .first()
    )
    if niche_retenue is None:
        niche_retenue = db.query(Niche).filter(Niche.campaign_id == campaign.id).first()
        if niche_retenue is not None:
            niche_retenue.statut = "retenue"

    niche_nom = niche_retenue.nom if niche_retenue else campaign.objectif
    produits = find_products(niche_nom)
    for p in produits:
        db.add(
            Product(
                campaign_id=campaign.id,
                nom=p["nom"],
                fournisseur=p["fournisseur"],
                prix_fournisseur=p["prix_fournisseur"],
                prix_conseille=p["prix_conseille"],
                marge_estimee=p["marge_estimee"],
                statut="propose",
            )
        )
    db.flush()
    return {"produits_proposes": len(produits), "niche": niche_nom}


def step_marque_creation(db: Session, campaign: Campaign) -> dict:
    produits = db.query(Product).filter(Product.campaign_id == campaign.id).all()
    niche = db.query(Niche).filter(Niche.campaign_id == campaign.id).first()
    niche_nom = niche.nom if niche else campaign.objectif

    brand_data = build_brand(niche_nom, [{"nom": p.nom} for p in produits])
    brand = Brand(
        campaign_id=campaign.id,
        nom=brand_data["nom"],
        slogan=brand_data["slogan"],
        palette_couleurs=brand_data["palette_couleurs"],
        logo_placeholder_url=brand_data["logo_placeholder_url"],
    )
    db.add(brand)
    db.flush()
    return {"marque": brand.nom, "slogan": brand.slogan}


def step_boutique_verification(db: Session, campaign: Campaign) -> dict:
    from backend.models.store import Store, StorePage

    store = db.query(Store).filter(Store.campaign_id == campaign.id).first()
    pages = db.query(StorePage).filter(StorePage.store_id == store.id).all() if store else []
    resultat = check_quality(store, pages)
    if store is not None:
        store.score_qualite = resultat["score_qualite"]
    db.flush()
    return resultat


def step_produits_import(db: Session, campaign: Campaign) -> dict:
    from backend.models.store import Store

    store = db.query(Store).filter(Store.campaign_id == campaign.id).first()
    brand = db.query(Brand).filter(Brand.campaign_id == campaign.id).first()
    produits = db.query(Product).filter(Product.campaign_id == campaign.id).all()

    inject_products_and_brand(db, store, brand, produits)
    for p in produits:
        p.statut = "importe"
    db.flush()
    return {"produits_importes": len(produits)}


def step_marketing_preparation(db: Session, campaign: Campaign) -> dict:
    brand = db.query(Brand).filter(Brand.campaign_id == campaign.id).first()
    produits = db.query(Product).filter(Product.campaign_id == campaign.id).all()

    brand_data = {
        "nom": brand.nom if brand else campaign.nom,
        "slogan": brand.slogan if brand else "",
    }
    assets = generate_marketing(brand_data, [{"nom": p.nom} for p in produits])
    for a in assets:
        db.add(
            MarketingAsset(
                campaign_id=campaign.id,
                type=a["type"],
                contenu=a["contenu"],
                statut="brouillon",
            )
        )
    db.flush()
    return {"assets_generes": len(assets)}


def step_ventes_preparation(db: Session, campaign: Campaign) -> dict:
    from backend.models.store import Store

    store = db.query(Store).filter(Store.campaign_id == campaign.id).first()
    if store is not None:
        store.statut = "publiee"
    campaign.statut = "publiee"

    from backend.payment_engine.engine import get_payment_engine

    providers_actifs = get_payment_engine().available_providers()
    db.flush()
    return {"boutique_publiee": True, "payment_providers_actifs": providers_actifs}


STEP_HANDLERS = {
    CampaignStep.NICHE_RECHERCHE: step_niche_recherche,
    CampaignStep.BOUTIQUE_INIT: step_boutique_init,
    CampaignStep.PRODUITS_RECHERCHE: step_produits_recherche,
    CampaignStep.MARQUE_CREATION: step_marque_creation,
    CampaignStep.BOUTIQUE_VERIFICATION: step_boutique_verification,
    CampaignStep.PRODUITS_IMPORT: step_produits_import,
    CampaignStep.MARKETING_PREPARATION: step_marketing_preparation,
    CampaignStep.VENTES_PREPARATION: step_ventes_preparation,
}
