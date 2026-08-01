from datetime import datetime

from pydantic import BaseModel


class OrderCreate(BaseModel):
    store_id: int
    client_nom: str
    client_contact: str
    montant: float


class OrderRead(BaseModel):
    id: int
    store_id: int
    client_nom: str
    client_contact: str
    montant: float
    statut: str
    date: datetime

    model_config = {"from_attributes": True}
