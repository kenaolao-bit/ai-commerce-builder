from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.order import Order
from backend.models.store import Store
from backend.schemas.order import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == payload.store_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Boutique introuvable")

    order = Order(
        store_id=payload.store_id,
        client_nom=payload.client_nom,
        client_contact=payload.client_contact,
        montant=payload.montant,
        statut="en_attente",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return order
