from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.brand import Brand
from backend.schemas.brand import BrandRead

router = APIRouter(prefix="/campaigns/{campaign_id}/brand", tags=["brand"])


@router.get("", response_model=BrandRead)
def get_brand(campaign_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.campaign_id == campaign_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Marque non encore creee pour cette campagne")
    return brand
