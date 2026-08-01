from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"), nullable=False, unique=True
    )
    nom_boutique: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), default="")
    statut: Mapped[str] = mapped_column(String(50), default="brouillon")
    score_qualite: Mapped[float] = mapped_column(default=0.0)

    campaign = relationship("Campaign", back_populates="store")
    pages = relationship("StorePage", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store", cascade="all, delete-orphan")


class StorePage(Base):
    __tablename__ = "store_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, default="")

    store = relationship("Store", back_populates="pages")
