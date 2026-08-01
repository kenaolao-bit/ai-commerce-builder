"""Module 2 - Product Finder (010_Product_Requirements, section 5).

Entree : niche retenue. Sortie J0 : 5-10 produits avec marge estimee
(generation assistee, sans scraping fournisseur reel - hors perimetre MVP).
"""

from backend.ai_engine._claude_client import ClaudeUnavailableError, ask_claude_json

PRODUCT_TEMPLATES = [
    ("Produit vedette {niche} - modele Pro", 1.6),
    ("Produit vedette {niche} - modele Standard", 1.5),
    ("Accessoire complementaire {niche} #1", 1.8),
    ("Accessoire complementaire {niche} #2", 1.7),
    ("Pack decouverte {niche}", 1.4),
    ("Edition premium {niche}", 2.0),
]

SYSTEM_PROMPT = (
    "Tu es un sourcing manager e-commerce. Reponds uniquement avec un tableau JSON de 5 a 10 "
    "objets, chacun avec les cles : nom, fournisseur, prix_fournisseur, prix_conseille, "
    "marge_estimee (tous les prix en FCFA/XOF)."
)


def _find_products_rules(niche_nom: str) -> list[dict]:
    produits = []
    for i, (template, marge_facteur) in enumerate(PRODUCT_TEMPLATES):
        prix_fournisseur = 3000 + i * 1500
        prix_conseille = round(prix_fournisseur * marge_facteur, -2)
        marge_estimee = round(prix_conseille - prix_fournisseur, 2)
        produits.append(
            {
                "nom": template.format(niche=niche_nom),
                "fournisseur": f"Fournisseur local {i + 1}",
                "prix_fournisseur": float(prix_fournisseur),
                "prix_conseille": float(prix_conseille),
                "marge_estimee": marge_estimee,
            }
        )
    return produits


def find_products(niche_nom: str) -> list[dict]:
    user_prompt = f"Niche retenue : {niche_nom}\nPropose des produits e-commerce vendables."
    try:
        data = ask_claude_json(SYSTEM_PROMPT, user_prompt)
        if isinstance(data, list) and data:
            return data
    except ClaudeUnavailableError:
        pass
    except Exception:
        pass

    return _find_products_rules(niche_nom)
