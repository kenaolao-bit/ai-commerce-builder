from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.marketing import MarketingAsset
from backend.schemas.marketing import MarketingAssetRead

router = APIRouter(prefix="/campaigns/{campaign_id}/marketing", tags=["marketing"])


@router.get("", response_model=list[MarketingAssetRead])
def list_marketing_assets(campaign_id: int, db: Session = Depends(get_db)):
    return db.query(MarketingAsset).filter(MarketingAsset.campaign_id == campaign_id).all()
