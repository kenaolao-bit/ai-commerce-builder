from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    fournisseur: Mapped[str] = mapped_column(String(255), default="")
    prix_fournisseur: Mapped[float] = mapped_column(default=0.0)
    prix_conseille: Mapped[float] = mapped_column(default=0.0)
    marge_estimee: Mapped[float] = mapped_column(default=0.0)
    statut: Mapped[str] = mapped_column(String(50), default="propose")

    campaign = relationship("Campaign", back_populates="products")
