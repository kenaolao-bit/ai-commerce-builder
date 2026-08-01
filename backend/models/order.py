from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    client_nom: Mapped[str] = mapped_column(String(255), nullable=False)
    client_contact: Mapped[str] = mapped_column(String(255), nullable=False)
    montant: Mapped[float] = mapped_column(default=0.0)
    statut: Mapped[str] = mapped_column(String(50), default="en_attente")
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    store = relationship("Store", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
