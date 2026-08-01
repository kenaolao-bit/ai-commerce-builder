"""Interface commune a tous les providers de paiement.

Regle d'architecture (020_System_Architecture, section 8 ; 030_Technical_Specification,
section 8) : le Commerce Engine et le reste de l'application ne parlent jamais a un
provider directement, uniquement a PaymentEngine. Chaque provider est un adaptateur
remplacable implementant PaymentProvider, y compris CinetPay qui n'est qu'un
connecteur parmi d'autres et ne doit jamais etre reference par la logique metier.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class PaymentResult:
    transaction_ref: str
    statut: PaymentStatus
    montant: float
    devise: str = "XOF"
    message: str = ""
    instructions: dict = field(default_factory=dict)


@dataclass
class PaymentEvent:
    transaction_ref: str
    statut: PaymentStatus
    montant: float | None = None
    raw: dict = field(default_factory=dict)


class PaymentProvider(ABC):
    """Adaptateur de paiement. Toute nouvelle methode de paiement (Mobile Money,
    carte, agregateur type CinetPay, workflow manuel) doit implementer cette
    interface pour rester interchangeable sans impact sur le Commerce Engine."""

    name: str = "base"

    @abstractmethod
    def initiate_payment(
        self, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult: ...

    @abstractmethod
    def check_status(self, transaction_ref: str) -> PaymentStatus: ...

    @abstractmethod
    def handle_webhook(self, payload: dict) -> PaymentEvent: ...
