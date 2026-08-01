from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order
from backend.models.payment import Payment
from backend.payment_engine.engine import UnknownPaymentProviderError, get_payment_engine
from backend.schemas.payment import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentRead,
    PaymentStatusRead,
    PaymentWebhookPayload,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/providers")
def list_providers():
    return {"providers": get_payment_engine().available_providers()}


@router.post("/initiate", response_model=PaymentInitiateResponse)
def initiate_payment(payload: PaymentInitiateRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    engine = get_payment_engine()
    try:
        result = engine.initiate_payment(
            payload.provider,
            order_id=str(order.id),
            amount=order.montant,
            currency=payload.currency,
            customer=payload.customer,
        )
    except UnknownPaymentProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payment = Payment(
        order_id=order.id,
        provider=payload.provider,
        transaction_ref=result.transaction_ref,
        statut=result.statut.value,
        montant=result.montant,
        devise=result.devise,
    )
    db.add(payment)
    if result.statut.value == "success":
        order.statut = "payee"
    db.commit()
    db.refresh(payment)

    return PaymentInitiateResponse(
        payment=payment, message=result.message, instructions=result.instructions
    )


@router.post("/webhook/{provider}")
def payment_webhook(provider: str, payload: PaymentWebhookPayload, db: Session = Depends(get_db)):
    engine = get_payment_engine()
    try:
        event = engine.handle_webhook(provider, payload.model_dump(exclude_none=True))
    except UnknownPaymentProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payment = (
        db.query(Payment)
        .filter(Payment.transaction_ref == event.transaction_ref, Payment.provider == provider)
        .first()
    )
    if payment is None:
        raise HTTPException(status_code=404, detail="Transaction inconnue")

    payment.statut = event.statut.value
    if event.statut.value == "success":
        order = db.query(Order).filter(Order.id == payment.order_id).first()
        if order is not None:
            order.statut = "payee"
    db.commit()
    db.refresh(payment)
    return PaymentRead.model_validate(payment)


@router.get("/{payment_id}/status", response_model=PaymentStatusRead)
def get_payment_status(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Paiement introuvable")

    engine = get_payment_engine()
    try:
        statut = engine.check_status(payment.provider, payment.transaction_ref)
        payment.statut = statut.value
        db.commit()
        db.refresh(payment)
    except UnknownPaymentProviderError:
        pass

    return PaymentStatusRead(payment=payment)
