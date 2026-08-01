"""Provider carte bancaire (Visa / Mastercard).

Simulation par defaut au J0. L'integration reelle (via CinetPay ou un
acquereur direct) remplacera le corps des methodes sans changer l'interface.
"""

import uuid

from backend.payment_engine.base import PaymentEvent, PaymentProvider, PaymentResult, PaymentStatus


class CardProvider(PaymentProvider):
    name = "card"

    def __init__(self, simulate: bool = True) -> None:
        self.simulate = simulate
        self._transactions: dict[str, PaymentStatus] = {}
        self._amounts: dict[str, float] = {}

    def initiate_payment(
        self, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult:
        transaction_ref = f"CARD-{order_id}-{uuid.uuid4().hex[:8]}"
        statut = PaymentStatus.SUCCESS if self.simulate else PaymentStatus.PENDING
        self._transactions[transaction_ref] = statut
        self._amounts[transaction_ref] = amount

        return PaymentResult(
            transaction_ref=transaction_ref,
            statut=statut,
            montant=amount,
            devise=currency,
            message="Transaction simulee carte (Visa/Mastercard)."
            if self.simulate
            else "Paiement initie.",
        )

    def check_status(self, transaction_ref: str) -> PaymentStatus:
        return self._transactions.get(transaction_ref, PaymentStatus.PENDING)

    def handle_webhook(self, payload: dict) -> PaymentEvent:
        transaction_ref = payload["transaction_ref"]
        statut = PaymentStatus(payload.get("statut", PaymentStatus.SUCCESS))
        self._transactions[transaction_ref] = statut

        return PaymentEvent(
            transaction_ref=transaction_ref,
            statut=statut,
            montant=self._amounts.get(transaction_ref),
            raw=payload,
        )
