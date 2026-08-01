from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"), nullable=False, unique=True
    )
    nom: Mapped[str] = mapped_column(String(255), nullable=False)
    slogan: Mapped[str] = mapped_column(String(500), default="")
    palette_couleurs: Mapped[dict] = mapped_column(JSON, default=dict)
    logo_placeholder_url: Mapped[str] = mapped_column(String(500), default="")

    campaign = relationship("Campaign", back_populates="brand")
