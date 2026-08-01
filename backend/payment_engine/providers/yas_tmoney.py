"""Provider YAS TMoney (Mobile Money, Togo).

Au J0, aucune integration API reelle : le provider fonctionne en mode
simulation (simulate=True) et genere des transactions fictives coherentes
pour permettre de tester tout le flux de vente. L'integration reelle
consistera a remplacer le corps de ces methodes par des appels a l'API YAS,
sans changer l'interface ni le reste du code (Commerce Engine, PaymentEngine).
"""

import uuid

from backend.payment_engine.base import PaymentEvent, PaymentProvider, PaymentResult, PaymentStatus


class YASTMoneyProvider(PaymentProvider):
    name = "yas_tmoney"

    def __init__(self, simulate: bool = True) -> None:
        self.simulate = simulate
        self._transactions: dict[str, PaymentStatus] = {}
        self._amounts: dict[str, float] = {}

    def initiate_payment(
        self, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult:
        transaction_ref = f"YAS-{order_id}-{uuid.uuid4().hex[:8]}"
        statut = PaymentStatus.SUCCESS if self.simulate else PaymentStatus.PENDING
        self._transactions[transaction_ref] = statut
        self._amounts[transaction_ref] = amount

        return PaymentResult(
            transaction_ref=transaction_ref,
            statut=statut,
            montant=amount,
            devise=currency,
            message="Transaction simulee YAS TMoney." if self.simulate else "Paiement initie.",
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
