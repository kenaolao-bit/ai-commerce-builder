from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    statut: Mapped[str] = mapped_column(String(50), default="pending")
    montant: Mapped[float] = mapped_column(default=0.0)
    devise: Mapped[str] = mapped_column(String(10), default="XOF")
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="payments")
