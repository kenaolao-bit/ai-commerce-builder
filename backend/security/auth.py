"""Authentification JWT admin (020_System_Architecture, section 12 ; Principe 11).

Utilisateur unique au MVP (Lao KENAO). Mot de passe hashe (bcrypt), jamais
stocke en clair en base. Le compte admin est cree automatiquement au demarrage
a partir de ADMIN_EMAIL / ADMIN_PASSWORD (.env, jamais commite).
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.security.secrets import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def ensure_admin_user(db: Session) -> User:
    settings = get_settings()
    admin = db.query(User).filter(User.email == settings.admin_email).first()
    if admin is None:
        admin = User(
            email=settings.admin_email,
            mot_de_passe_hash=hash_password(settings.admin_password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin


def authenticate_admin(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.mot_de_passe_hash):
        return None
    return user


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Identifiants invalides ou expires",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    if token is None:
        raise CREDENTIALS_EXCEPTION

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError as exc:
        raise CREDENTIALS_EXCEPTION from exc

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user
