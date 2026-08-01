import pytest

from backend.commerce_engine.engine import CampaignAlreadyCompletedError, CommerceEngine
from backend.models.brand import Brand
from backend.models.marketing import MarketingAsset
from backend.models.niche import Niche
from backend.models.product import Product
from backend.models.store import Store, StorePage


def _create_campaign(db_session):
    engine = CommerceEngine()
    return engine, engine.create_campaign(
        db_session,
        nom="Boutique Test",
        pays_cible="Togo",
        langue="fr",
        budget=200000,
        objectif="vendre des accessoires mobiles",
    )


def test_campaign_progresses_through_8_steps_in_order(db_session):
    engine, campaign = _create_campaign(db_session)
    assert campaign.etape_courante == 1

    for etape_attendue in range(1, 9):
        result = engine.advance(db_session, campaign)
        assert result["etape_executee"] == etape_attendue

    assert campaign.etape_courante == 9
    assert campaign.statut == "publiee"


def test_advance_populates_expected_database_rows(db_session):
    engine, campaign = _create_campaign(db_session)
    for _ in range(8):
        engine.advance(db_session, campaign)

    assert db_session.query(Niche).filter_by(campaign_id=campaign.id).count() >= 3
    assert db_session.query(Product).filter_by(campaign_id=campaign.id).count() >= 1
    assert db_session.query(Brand).filter_by(campaign_id=campaign.id).count() == 1

    store = db_session.query(Store).filter_by(campaign_id=campaign.id).first()
    assert store is not None
    assert store.statut == "publiee"
    assert db_session.query(StorePage).filter_by(store_id=store.id).count() == 7

    assert db_session.query(MarketingAsset).filter_by(campaign_id=campaign.id).count() >= 1


def test_advance_raises_once_all_steps_are_completed(db_session):
    engine, campaign = _create_campaign(db_session)
    for _ in range(8):
        engine.advance(db_session, campaign)

    with pytest.raises(CampaignAlreadyCompletedError):
        engine.advance(db_session, campaign)
