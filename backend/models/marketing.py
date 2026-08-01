from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class MarketingAsset(Base):
    __tablename__ = "marketing_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    contenu: Mapped[str] = mapped_column(Text, default="")
    statut: Mapped[str] = mapped_column(String(50), default="brouillon")

    campaign = relationship("Campaign", back_populates="marketing_assets")
