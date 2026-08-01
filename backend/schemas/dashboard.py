from pydantic import BaseModel


class CampaignProgress(BaseModel):
    id: int
    nom: str
    statut: str
    etape_courante: int
    total_etapes: int = 8


class DashboardKPIs(BaseModel):
    chiffre_affaires_total: float
    nombre_ventes: int
    nombre_commandes: int
    produits_actifs: int
    campagnes: list[CampaignProgress]
    alertes: list[str]
