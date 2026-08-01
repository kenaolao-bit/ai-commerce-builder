"""Commerce Engine : orchestrateur central des campagnes (020_System_Architecture, section 4).

Le Commerce Engine est le coeur du systeme. Il pilote la machine a etats des
8 etapes par campagne et est le seul point d'entree vers les modules IA, le
Store Builder et le Payment Engine pour tout ce qui concerne le cycle de vie
d'une campagne.
"""

from sqlalchemy.orm import Session

from backend.commerce_engine.steps import STEP_HANDLERS, STEP_LABELS, CampaignStep
from backend.models.campaign import Campaign


class CampaignAlreadyCompletedError(Exception):
    pass


class CommerceEngine:
    TOTAL_STEPS = len(CampaignStep)

    def create_campaign(self, db: Session, **kwargs) -> Campaign:
        campaign = Campaign(**kwargs, statut="active", etape_courante=1)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def advance(self, db: Session, campaign: Campaign) -> dict:
        if campaign.etape_courante > self.TOTAL_STEPS:
            raise CampaignAlreadyCompletedError(
                f"La campagne {campaign.id} a deja termine ses {self.TOTAL_STEPS} etapes."
            )

        etape = CampaignStep(campaign.etape_courante)
        handler = STEP_HANDLERS[etape]

        try:
            resultat = handler(db, campaign)
        except Exception:
            db.rollback()
            raise

        etape_executee = int(etape)
        if campaign.etape_courante <= self.TOTAL_STEPS:
            campaign.etape_courante = min(etape_executee + 1, self.TOTAL_STEPS + 1)
        if campaign.etape_courante > self.TOTAL_STEPS and campaign.statut == "active":
            campaign.statut = "publiee"

        db.commit()
        db.refresh(campaign)

        return {
            "etape_executee": etape_executee,
            "etape_label": STEP_LABELS[etape],
            "resultat": resultat,
        }


_engine_instance: CommerceEngine | None = None


def get_commerce_engine() -> CommerceEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = CommerceEngine()
    return _engine_instance
