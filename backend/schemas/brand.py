from pydantic import BaseModel


class BrandRead(BaseModel):
    id: int
    campaign_id: int
    nom: str
    slogan: str
    palette_couleurs: dict
    logo_placeholder_url: str

    model_config = {"from_attributes": True}
