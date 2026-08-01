from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    pays_cible: Mapped[str] = mapped_column(String(100), nullable=False)
    langue: Mapped[str] = mapped_column(String(50), nullable=False)
    budget: Mapped[float] = mapped_column(default=0.0)
    objectif: Mapped[str] = mapped_column(String(255), nullable=False)
    statut: Mapped[str] = mapped_column(String(50), default="active")
    etape_courante: Mapped[int] = mapped_column(Integer, default=1)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    niches = relationship("Niche", back_populates="campaign", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="campaign", cascade="all, delete-orphan")
    brand = relationship(
        "Brand", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )
    store = relationship(
        "Store", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )
    marketing_assets = relationship(
        "MarketingAsset", back_populates="campaign", cascade="all, delete-orphan"
    )
