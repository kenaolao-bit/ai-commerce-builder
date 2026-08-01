from pydantic import BaseModel


class MarketingAssetRead(BaseModel):
    id: int
    campaign_id: int
    type: str
    contenu: str
    statut: str

    model_config = {"from_attributes": True}
