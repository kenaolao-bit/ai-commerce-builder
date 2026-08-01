from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.niche import Niche
from backend.schemas.niche import NicheRead, NicheSelect

router = APIRouter(prefix="/campaigns/{campaign_id}/niches", tags=["niches"])


@router.get("", response_model=list[NicheRead])
def list_niches(campaign_id: int, db: Session = Depends(get_db)):
    return db.query(Niche).filter(Niche.campaign_id == campaign_id).all()


@router.post("/select", response_model=NicheRead)
def select_niche(campaign_id: int, payload: NicheSelect, db: Session = Depends(get_db)):
    niche = (
        db.query(Niche)
        .filter(Niche.id == payload.niche_id, Niche.campaign_id == campaign_id)
        .first()
    )
    if niche is None:
        raise HTTPException(status_code=404, detail="Niche introuvable pour cette campagne")

    db.query(Niche).filter(Niche.campaign_id == campaign_id).update({"statut": "proposee"})
    niche.statut = "retenue"
    db.commit()
    db.refresh(niche)
    return niche
