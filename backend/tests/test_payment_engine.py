import pytest

from backend.payment_engine.base import PaymentStatus
from backend.payment_engine.engine import PaymentEngine, UnknownPaymentProviderError
from backend.security.secrets import Settings


def make_engine(providers: str = "manual,yas_tmoney,moov_money,card", simulate: bool = True) -> PaymentEngine:
    settings = Settings(
        _env_file=None, payment_provider_active=providers, payment_simulate=simulate
    )
    return PaymentEngine(settings=settings)


def test_simulated_provider_returns_success_immediately():
    engine = make_engine(simulate=True)
    result = engine.initiate_payment(
        "yas_tmoney", order_id="1", amount=1000, currency="XOF", customer={}
    )
    assert result.statut == PaymentStatus.SUCCESS
    assert engine.check_status("yas_tmoney", result.transaction_ref) == PaymentStatus.SUCCESS


def test_manual_workflow_starts_pending_and_is_confirmed_via_webhook():
    engine = make_engine()
    result = engine.initiate_payment(
        "manual", order_id="2", amount=5000, currency="XOF", customer={"nom": "Client"}
    )
    assert result.statut == PaymentStatus.PENDING
    assert engine.check_status("manual", result.transaction_ref) == PaymentStatus.PENDING
    assert "message" in result.instructions

    event = engine.handle_webhook(
        "manual", {"transaction_ref": result.transaction_ref, "action": "confirm"}
    )
    assert event.statut == PaymentStatus.SUCCESS
    assert engine.check_status("manual", result.transaction_ref) == PaymentStatus.SUCCESS


def test_manual_workflow_can_be_rejected():
    engine = make_engine()
    result = engine.initiate_payment("manual", order_id="3", amount=2000, currency="XOF", customer={})
    event = engine.handle_webhook(
        "manual", {"transaction_ref": result.transaction_ref, "action": "reject"}
    )
    assert event.statut == PaymentStatus.FAILED


def test_inactive_or_unknown_provider_raises():
    engine = make_engine(providers="manual")
    with pytest.raises(UnknownPaymentProviderError):
        engine.initiate_payment("cinetpay", order_id="4", amount=100, currency="XOF", customer={})


def test_cinetpay_is_not_active_by_default():
    settings = Settings(_env_file=None)
    assert "cinetpay" not in settings.active_payment_providers
