from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Niche(Base):
    __tablename__ = "niches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    score_opportunite: Mapped[float] = mapped_column(default=0.0)
    niveau_concurrence: Mapped[str] = mapped_column(String(50), default="moyen")
    recommandation: Mapped[str] = mapped_column(String(1000), default="")
    statut: Mapped[str] = mapped_column(String(50), default="proposee")

    campaign = relationship("Campaign", back_populates="niches")
