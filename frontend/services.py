"""Passerelle directe entre Streamlit et le backend, sans appel HTTP.

Streamlit Community Cloud ne lance qu'un seul processus Python (le fichier
principal `frontend/app.py`) : il n'y a pas de serveur FastAPI separe a
joindre sur un port. Ce module appelle donc directement les fonctions de
`backend/api/*.py` (ou sont deja isolees les logiques metier : Commerce
Engine, AI Engine, Payment Engine, requetes SQLAlchemy) en leur passant une
session de base de donnees explicite, sans passer par le routing FastAPI.

Les modules `backend/api/*.py` et `backend/main.py` restent inchanges et
utilisables tels quels pour exposer une API REST externe en Phase 2 (il
suffira de les lancer avec un serveur ASGI comme aujourd'hui) ; ce module ne
fait que les reutiliser directement en appel de fonction.

Toutes les fonctions ci-dessous retournent des dict/list[dict] (via
`.model_dump(mode="json")`) pour que les pages Streamlit consomment des
donnees de meme forme qu'avec l'ancienne couche HTTP.
"""

from contextlib import contextmanager

import streamlit as st
from fastapi import HTTPException

from backend.api import brand as brand_api
from backend.api import campaigns as campaigns_api
from backend.api import dashboard as dashboard_api
from backend.api import marketing as marketing_api
from backend.api import niches as niches_api
from backend.api import orders as orders_api
from backend.api import payments as payments_api
from backend.api import products as products_api
from backend.api import quality as quality_api
from backend.api import store as store_api
from backend.database import SessionLocal, init_db
from backend.schemas.brand import BrandRead
from backend.schemas.campaign import CampaignCreate, CampaignRead
from backend.schemas.marketing import MarketingAssetRead
from backend.schemas.niche import NicheRead, NicheSelect
from backend.schemas.order import OrderCreate, OrderRead
from backend.schemas.payment import PaymentInitiateRequest, PaymentWebhookPayload
from backend.schemas.product import ProductImportRequest, ProductRead
from backend.schemas.store import StoreRead
from backend.security.auth import authenticate_admin, ensure_admin_user


@contextmanager
def _session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except HTTPException as exc:
        raise RuntimeError(exc.detail) from exc


def _dump(obj, schema) -> dict:
    return schema.model_validate(obj).model_dump(mode="json")


def _dump_list(objs, schema) -> list[dict]:
    return [schema.model_validate(o).model_dump(mode="json") for o in objs]


@st.cache_resource(show_spinner=False)
def ensure_initialized() -> bool:
    init_db()
    with _session() as db:
        ensure_admin_user(db)
    return True


def login(email: str, password: str) -> bool:
    with _session() as db:
        return authenticate_admin(db, email, password) is not None


def list_campaigns() -> list[dict]:
    with _session() as db:
        return _dump_list(_call(campaigns_api.list_campaigns, db=db), CampaignRead)


def create_campaign(nom: str, pays_cible: str, langue: str, budget: float, objectif: str) -> dict:
    payload = CampaignCreate(nom=nom, pays_cible=pays_cible, langue=langue, budget=budget, objectif=objectif)
    with _session() as db:
        campaign = _call(campaigns_api.create_campaign, payload, db=db)
        return _dump(campaign, CampaignRead)


def advance_campaign(campaign_id: int) -> dict:
    with _session() as db:
        result = _call(campaigns_api.advance_campaign, campaign_id, db=db)
        return result.model_dump(mode="json")


def list_niches(campaign_id: int) -> list[dict]:
    with _session() as db:
        return _dump_list(_call(niches_api.list_niches, campaign_id, db=db), NicheRead)


def select_niche(campaign_id: int, niche_id: int) -> dict:
    with _session() as db:
        niche = _call(niches_api.select_niche, campaign_id, NicheSelect(niche_id=niche_id), db=db)
        return _dump(niche, NicheRead)


def list_products(campaign_id: int) -> list[dict]:
    with _session() as db:
        return _dump_list(_call(products_api.list_products, campaign_id, db=db), ProductRead)


def import_products(campaign_id: int, product_ids: list[int]) -> list[dict]:
    payload = ProductImportRequest(product_ids=product_ids)
    with _session() as db:
        produits = _call(products_api.import_products, campaign_id, payload, db=db)
        return _dump_list(produits, ProductRead)


def get_brand(campaign_id: int) -> dict | None:
    with _session() as db:
        try:
            brand = _call(brand_api.get_brand, campaign_id, db=db)
        except RuntimeError:
            return None
        return _dump(brand, BrandRead)


def get_store(campaign_id: int) -> dict | None:
    with _session() as db:
        try:
            store = _call(store_api.get_store, campaign_id, db=db)
        except RuntimeError:
            return None
        return _dump(store, StoreRead)


def get_store_quality(campaign_id: int) -> dict | None:
    with _session() as db:
        try:
            return _call(quality_api.get_store_quality, campaign_id, db=db)
        except RuntimeError:
            return None


def list_marketing_assets(campaign_id: int) -> list[dict]:
    with _session() as db:
        return _dump_list(_call(marketing_api.list_marketing_assets, campaign_id, db=db), MarketingAssetRead)


def create_order(store_id: int, client_nom: str, client_contact: str, montant: float) -> dict:
    payload = OrderCreate(
        store_id=store_id, client_nom=client_nom, client_contact=client_contact, montant=montant
    )
    with _session() as db:
        order = _call(orders_api.create_order, payload, db=db)
        return _dump(order, OrderRead)


def list_payment_providers() -> list[str]:
    return _call(payments_api.list_providers)["providers"]


def initiate_payment(order_id: int, provider: str, currency: str = "XOF", customer: dict | None = None) -> dict:
    payload = PaymentInitiateRequest(order_id=order_id, provider=provider, currency=currency, customer=customer or {})
    with _session() as db:
        result = _call(payments_api.initiate_payment, payload, db=db)
        return result.model_dump(mode="json")


def confirm_manual_payment(transaction_ref: str, action: str) -> dict:
    payload = PaymentWebhookPayload(transaction_ref=transaction_ref, action=action)
    with _session() as db:
        payment = _call(payments_api.payment_webhook, "manual", payload, db=db)
        return payment.model_dump(mode="json")


def get_dashboard_kpis() -> dict:
    with _session() as db:
        kpis = _call(dashboard_api.get_kpis, db=db)
        return kpis.model_dump(mode="json")
