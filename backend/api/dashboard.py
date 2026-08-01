from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.campaign import Campaign
from backend.models.order import Order
from backend.models.payment import Payment
from backend.models.product import Product
from backend.schemas.dashboard import CampaignProgress, DashboardKPIs

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def get_kpis(db: Session = Depends(get_db)):
    chiffre_affaires_total = (
        db.query(func.coalesce(func.sum(Payment.montant), 0.0))
        .filter(Payment.statut == "success")
        .scalar()
    )
    nombre_ventes = db.query(Order).filter(Order.statut == "payee").count()
    nombre_commandes = db.query(Order).count()
    produits_actifs = db.query(Product).filter(Product.statut == "importe").count()

    campagnes = [
        CampaignProgress(
            id=c.id, nom=c.nom, statut=c.statut, etape_courante=min(c.etape_courante, 8)
        )
        for c in db.query(Campaign).order_by(Campaign.id.desc()).all()
    ]

    alertes = []
    paiements_echec = db.query(Payment).filter(Payment.statut == "failed").count()
    if paiements_echec:
        alertes.append(f"{paiements_echec} paiement(s) en echec necessitent une verification.")

    commandes_en_attente = db.query(Order).filter(Order.statut == "en_attente").count()
    if commandes_en_attente:
        alertes.append(f"{commandes_en_attente} commande(s) en attente de paiement.")

    campagnes_bloquees = [c for c in campagnes if c.statut == "active" and c.etape_courante == 8]
    if campagnes_bloquees:
        alertes.append(
            f"{len(campagnes_bloquees)} campagne(s) a l'etape 8/8 en attente de publication."
        )

    return DashboardKPIs(
        chiffre_affaires_total=float(chiffre_affaires_total or 0.0),
        nombre_ventes=nombre_ventes,
        nombre_commandes=nombre_commandes,
        produits_actifs=produits_actifs,
        campagnes=campagnes,
        alertes=alertes,
    )
