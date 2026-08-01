from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.auth import LoginRequest, TokenResponse
from backend.security.auth import authenticate_admin, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_admin(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)
