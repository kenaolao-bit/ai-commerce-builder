"""Point d'entree FastAPI (020_System_Architecture, section 3)."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from backend.api import auth, brand, campaigns, dashboard, marketing, niches, orders, payments, products, quality, store
from backend.database import SessionLocal, init_db
from backend.security.auth import ensure_admin_user, get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        ensure_admin_user(db)
    finally:
        db.close()
    yield


app = FastAPI(title="AI Commerce Builder", version="1.0.0", lifespan=lifespan)

protected = [Depends(get_current_user)]

app.include_router(auth.router)
app.include_router(campaigns.router, dependencies=protected)
app.include_router(niches.router, dependencies=protected)
app.include_router(products.router, dependencies=protected)
app.include_router(brand.router, dependencies=protected)
app.include_router(quality.router, dependencies=protected)
app.include_router(store.router, dependencies=protected)
app.include_router(marketing.router, dependencies=protected)
app.include_router(orders.router, dependencies=protected)
app.include_router(payments.router, dependencies=protected)
app.include_router(dashboard.router, dependencies=protected)


@app.get("/health")
def health():
    return {"statut": "ok"}
