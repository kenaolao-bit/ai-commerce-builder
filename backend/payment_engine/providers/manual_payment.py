"""Workflow de paiement manuel.

Contexte marche togolais (Principe 4) : tant que le compte marchand CinetPay
n'est pas valide, le client paie par Mobile Money ou virement direct et
transmet une preuve ; l'administrateur (Lao KENAO) confirme manuellement la
transaction depuis le Dashboard CEO. Ce provider modelise ce flux via
l'interface PaymentProvider commune, exactement comme un provider automatise :
la confirmation admin est traitee comme un "webhook" interne (handle_webhook),
ce qui evite toute branche de code specifique dans le Commerce Engine.
"""

import uuid

from backend.payment_engine.base import PaymentEvent, PaymentProvider, PaymentResult, PaymentStatus


class ManualPaymentProvider(PaymentProvider):
    name = "manual"

    INSTRUCTIONS_TEMPLATE = (
        "Effectuez le paiement de {amount} {currency} par Mobile Money (YAS TMoney / "
        "Moov Money) ou virement, puis transmettez la preuve de paiement a "
        "l'administrateur avec la reference {ref}."
    )

    def __init__(self) -> None:
        self._transactions: dict[str, PaymentStatus] = {}
        self._amounts: dict[str, float] = {}

    def initiate_payment(
        self, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult:
        transaction_ref = f"MANUAL-{order_id}-{uuid.uuid4().hex[:8]}"
        self._transactions[transaction_ref] = PaymentStatus.PENDING
        self._amounts[transaction_ref] = amount

        instructions = {
            "message": self.INSTRUCTIONS_TEMPLATE.format(
                amount=amount, currency=currency, ref=transaction_ref
            ),
            "canaux": ["yas_tmoney", "moov_money", "virement"],
        }
        return PaymentResult(
            transaction_ref=transaction_ref,
            statut=PaymentStatus.PENDING,
            montant=amount,
            devise=currency,
            message="En attente de confirmation manuelle par l'administrateur.",
            instructions=instructions,
        )

    def check_status(self, transaction_ref: str) -> PaymentStatus:
        return self._transactions.get(transaction_ref, PaymentStatus.PENDING)

    def handle_webhook(self, payload: dict) -> PaymentEvent:
        """Recoit la confirmation (ou le rejet) saisie par l'administrateur.

        payload attendu : {"transaction_ref": str, "action": "confirm"|"reject"}
        """
        transaction_ref = payload["transaction_ref"]
        action = payload.get("action", "confirm")
        statut = PaymentStatus.SUCCESS if action == "confirm" else PaymentStatus.FAILED
        self._transactions[transaction_ref] = statut

        return PaymentEvent(
            transaction_ref=transaction_ref,
            statut=statut,
            montant=self._amounts.get(transaction_ref),
            raw=payload,
        )
