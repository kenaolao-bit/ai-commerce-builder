from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.ai_engine.quality_checker import check_quality
from backend.database import get_db
from backend.models.store import Store, StorePage

router = APIRouter(prefix="/campaigns/{campaign_id}/store/quality", tags=["quality"])


@router.get("")
def get_store_quality(campaign_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.campaign_id == campaign_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Boutique non encore initialisee")

    pages = db.query(StorePage).filter(StorePage.store_id == store.id).all()
    return check_quality(store, pages)
