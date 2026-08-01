"""Provider CinetPay (agregateur Mobile Money + carte).

Non actif au J0 (absent de PAYMENT_PROVIDER_ACTIVE par defaut) : le compte
marchand n'est pas encore valide. Ce fichier est pret a etre branche des
validation en ajoutant "cinetpay" a PAYMENT_PROVIDER_ACTIVE dans .env et en
renseignant CINETPAY_API_KEY / CINETPAY_SITE_ID / CINETPAY_ENABLED=true.
Aucune autre modification du code n'est necessaire : le reste de l'application
ne connait que l'interface PaymentProvider via PaymentEngine.
"""

import uuid

from backend.payment_engine.base import PaymentEvent, PaymentProvider, PaymentResult, PaymentStatus


class CinetPayProvider(PaymentProvider):
    name = "cinetpay"

    def __init__(self, api_key: str = "", site_id: str = "", simulate: bool = True) -> None:
        self.api_key = api_key
        self.site_id = site_id
        self.simulate = simulate
        self._transactions: dict[str, PaymentStatus] = {}
        self._amounts: dict[str, float] = {}

    def initiate_payment(
        self, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult:
        transaction_ref = f"CINETPAY-{order_id}-{uuid.uuid4().hex[:8]}"
        # L'appel reel a l'API CinetPay (endpoint /v2/payment) sera branche ici
        # une fois le compte marchand valide ; en attendant, comportement simule
        # identique aux autres providers pour rester testable de bout en bout.
        statut = PaymentStatus.SUCCESS if self.simulate else PaymentStatus.PENDING
        self._transactions[transaction_ref] = statut
        self._amounts[transaction_ref] = amount

        return PaymentResult(
            transaction_ref=transaction_ref,
            statut=statut,
            montant=amount,
            devise=currency,
            message="Transaction simulee CinetPay." if self.simulate else "Paiement initie.",
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
