from pydantic import BaseModel


class NicheRead(BaseModel):
    id: int
    campaign_id: int
    nom: str
    score_opportunite: float
    niveau_concurrence: str
    recommandation: str
    statut: str

    model_config = {"from_attributes": True}


class NicheSelect(BaseModel):
    niche_id: int
