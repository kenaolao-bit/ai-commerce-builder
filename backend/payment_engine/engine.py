"""Orchestrateur du Payment Engine.

Point d'entree unique pour tout paiement dans l'application. Le Commerce
Engine, les endpoints API et le frontend ne doivent jamais importer un
provider directement (ni CinetPay, ni les autres) : ils passent toujours par
PaymentEngine, qui selectionne le provider actif via la configuration
(.env : PAYMENT_PROVIDER_ACTIVE). Ajouter/retirer/remplacer un moyen de
paiement se fait en modifiant cette liste, sans toucher au reste du code.
"""

from typing import Callable

from backend.payment_engine.base import PaymentEvent, PaymentProvider, PaymentResult, PaymentStatus
from backend.payment_engine.providers import (
    CardProvider,
    CinetPayProvider,
    ManualPaymentProvider,
    MoovMoneyProvider,
    YASTMoneyProvider,
)
from backend.security.secrets import Settings, get_settings

ProviderFactory = Callable[[Settings], PaymentProvider]

PROVIDER_REGISTRY: dict[str, ProviderFactory] = {
    "manual": lambda settings: ManualPaymentProvider(),
    "yas_tmoney": lambda settings: YASTMoneyProvider(simulate=settings.payment_simulate),
    "moov_money": lambda settings: MoovMoneyProvider(simulate=settings.payment_simulate),
    "card": lambda settings: CardProvider(simulate=settings.payment_simulate),
    "cinetpay": lambda settings: CinetPayProvider(
        api_key=settings.cinetpay_api_key,
        site_id=settings.cinetpay_site_id,
        simulate=settings.payment_simulate,
    ),
}


class UnknownPaymentProviderError(ValueError):
    pass


class PaymentEngine:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._providers: dict[str, PaymentProvider] = {}
        for provider_name in self.settings.active_payment_providers:
            factory = PROVIDER_REGISTRY.get(provider_name)
            if factory is not None:
                self._providers[provider_name] = factory(self.settings)

    def available_providers(self) -> list[str]:
        return list(self._providers.keys())

    def _get_provider(self, provider_name: str) -> PaymentProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            raise UnknownPaymentProviderError(
                f"Provider de paiement inconnu ou inactif : '{provider_name}'. "
                f"Providers actifs : {self.available_providers()}"
            )
        return provider

    def initiate_payment(
        self, provider_name: str, order_id: str, amount: float, currency: str, customer: dict
    ) -> PaymentResult:
        provider = self._get_provider(provider_name)
        return provider.initiate_payment(order_id, amount, currency, customer)

    def check_status(self, provider_name: str, transaction_ref: str) -> PaymentStatus:
        provider = self._get_provider(provider_name)
        return provider.check_status(transaction_ref)

    def handle_webhook(self, provider_name: str, payload: dict) -> PaymentEvent:
        provider = self._get_provider(provider_name)
        return provider.handle_webhook(payload)


_engine_instance: PaymentEngine | None = None


def get_payment_engine() -> PaymentEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PaymentEngine()
    return _engine_instance
