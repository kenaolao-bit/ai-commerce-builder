from datetime import datetime

from pydantic import BaseModel


class PaymentInitiateRequest(BaseModel):
    order_id: int
    provider: str
    currency: str = "XOF"
    customer: dict = {}


class PaymentRead(BaseModel):
    id: int
    order_id: int
    provider: str
    transaction_ref: str
    statut: str
    montant: float
    devise: str
    date: datetime

    model_config = {"from_attributes": True}


class PaymentInitiateResponse(BaseModel):
    payment: PaymentRead
    message: str = ""
    instructions: dict = {}


class PaymentWebhookPayload(BaseModel):
    transaction_ref: str
    action: str | None = None
    statut: str | None = None

    model_config = {"extra": "allow"}


class PaymentStatusRead(BaseModel):
    payment: PaymentRead
