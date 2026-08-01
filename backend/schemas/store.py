from pydantic import BaseModel


class StorePageRead(BaseModel):
    id: int
    type: str
    contenu: str

    model_config = {"from_attributes": True}


class StoreRead(BaseModel):
    id: int
    campaign_id: int
    nom_boutique: str
    url: str
    statut: str
    score_qualite: float
    pages: list[StorePageRead] = []

    model_config = {"from_attributes": True}
