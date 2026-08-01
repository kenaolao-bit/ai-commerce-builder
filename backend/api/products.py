from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.product import Product
from backend.schemas.product import ProductImportRequest, ProductRead

router = APIRouter(prefix="/campaigns/{campaign_id}/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(campaign_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.campaign_id == campaign_id).all()


@router.post("/import", response_model=list[ProductRead])
def import_products(campaign_id: int, payload: ProductImportRequest, db: Session = Depends(get_db)):
    produits = (
        db.query(Product)
        .filter(Product.campaign_id == campaign_id, Product.id.in_(payload.product_ids))
        .all()
    )
    for p in produits:
        p.statut = "importe"
    db.commit()
    for p in produits:
        db.refresh(p)
    return produits
