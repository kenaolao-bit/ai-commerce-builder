"""Module 1 - Niche Finder (010_Product_Requirements, section 5).

Entrees : pays cible, langue, budget, objectif.
Sortie J0 (MVP, section 6 de la spec technique) : 3-5 niches scorees.
Utilise un prompt Claude structure si une cle API est configuree, sinon des
regles deterministes garantissant un resultat exploitable dans tous les cas.
"""

from backend.ai_engine._claude_client import ClaudeUnavailableError, ask_claude_json

BASE_NICHES = [
    ("Accessoires mobiles & gadgets tech", "electronique", "elevee"),
    ("Beaute et soins capillaires naturels", "beaute", "moyenne"),
    ("Mode et accessoires femme", "mode", "elevee"),
    ("Articles pour bebes et jeunes parents", "famille", "moyenne"),
    ("Petit electromenager et maison connectee", "maison", "faible"),
    ("Fitness et bien-etre a domicile", "sport", "moyenne"),
]

SYSTEM_PROMPT = (
    "Tu es un analyste e-commerce specialise sur l'Afrique de l'Ouest. "
    "Reponds uniquement avec un tableau JSON de 3 a 5 objets, chacun avec les cles : "
    "nom, score_opportunite (0-100), niveau_concurrence (faible/moyenne/elevee), recommandation."
)


def _find_niches_rules(pays_cible: str, langue: str, budget: float, objectif: str) -> list[dict]:
    budget_facteur = min(max(budget / 500_000, 0.3), 1.5) if budget else 0.8
    niches = []
    for i, (nom, categorie, concurrence) in enumerate(BASE_NICHES[:5]):
        score_base = 90 - i * 8
        score = round(score_base * budget_facteur, 1)
        score = max(min(score, 99.0), 10.0)
        niches.append(
            {
                "nom": nom,
                "score_opportunite": score,
                "niveau_concurrence": concurrence,
                "recommandation": (
                    f"Niche '{nom}' pertinente pour {pays_cible} ({langue}), categorie "
                    f"{categorie}, alignee avec l'objectif '{objectif}' et un budget de "
                    f"{budget:,.0f}."
                ),
            }
        )
    return niches


def find_niches(pays_cible: str, langue: str, budget: float, objectif: str) -> list[dict]:
    user_prompt = (
        f"Pays cible: {pays_cible}\nLangue: {langue}\nBudget: {budget}\nObjectif: {objectif}\n"
        "Propose des niches e-commerce rentables adaptees a ce contexte."
    )
    try:
        data = ask_claude_json(SYSTEM_PROMPT, user_prompt)
        if isinstance(data, list) and data:
            return data
    except ClaudeUnavailableError:
        pass
    except Exception:
        pass

    return _find_niches_rules(pays_cible, langue, budget, objectif)
