from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.commerce_engine.engine import CampaignAlreadyCompletedError, get_commerce_engine
from backend.database import get_db
from backend.models.campaign import Campaign
from backend.schemas.campaign import CampaignAdvanceResult, CampaignCreate, CampaignRead

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _get_campaign_or_404(db: Session, campaign_id: int) -> Campaign:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campagne introuvable")
    return campaign


@router.post("", response_model=CampaignRead)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    engine = get_commerce_engine()
    campaign = engine.create_campaign(db, **payload.model_dump())
    return campaign


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    return _get_campaign_or_404(db, campaign_id)


@router.get("", response_model=list[CampaignRead])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.id.desc()).all()


@router.post("/{campaign_id}/advance", response_model=CampaignAdvanceResult)
def advance_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = _get_campaign_or_404(db, campaign_id)
    engine = get_commerce_engine()
    try:
        outcome = engine.advance(db, campaign)
    except CampaignAlreadyCompletedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CampaignAdvanceResult(
        campaign=campaign,
        etape_executee=outcome["etape_executee"],
        resultat={"label": outcome["etape_label"], **outcome["resultat"]},
    )
