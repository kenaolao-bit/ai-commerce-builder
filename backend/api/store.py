from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.store import Store
from backend.schemas.store import StoreRead

router = APIRouter(prefix="/campaigns/{campaign_id}/store", tags=["store"])


@router.get("", response_model=StoreRead)
def get_store(campaign_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.campaign_id == campaign_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Boutique non encore initialisee")
    return store
