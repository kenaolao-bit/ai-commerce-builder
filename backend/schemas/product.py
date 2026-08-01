from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    campaign_id: int
    nom: str
    fournisseur: str
    prix_fournisseur: float
    prix_conseille: float
    marge_estimee: float
    statut: str

    model_config = {"from_attributes": True}


class ProductImportRequest(BaseModel):
    product_ids: list[int]
