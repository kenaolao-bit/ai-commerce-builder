from datetime import datetime

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    nom: str
    pays_cible: str = "Togo"
    langue: str = "fr"
    budget: float = Field(default=0.0, ge=0)
    objectif: str


class CampaignRead(BaseModel):
    id: int
    nom: str
    pays_cible: str
    langue: str
    budget: float
    objectif: str
    statut: str
    etape_courante: int
    date_creation: datetime

    model_config = {"from_attributes": True}


class CampaignAdvanceResult(BaseModel):
    campaign: CampaignRead
    etape_executee: int
    resultat: dict
