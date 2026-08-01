"""Connexion et session SQLAlchemy.

MVP : SQLite. Le choix de SQLAlchemy permet une migration ulterieure vers
PostgreSQL (Phase 2) en ne changeant que DATABASE_URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.security.secrets import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cree les tables manquantes. Sert de migration initiale pour le MVP."""
    from backend import models  # noqa: F401 (assure l'enregistrement des modeles)

    Base.metadata.create_all(bind=engine)
