"""Module 3 - Brand Builder (010_Product_Requirements, section 5).

Genere : nom, slogan, palette de couleurs, logo (placeholder MVP).
"""

import hashlib

from backend.ai_engine._claude_client import ClaudeUnavailableError, ask_claude_json

PALETTES = [
    {"primaire": "#1B4332", "secondaire": "#40916C", "accent": "#D8F3DC"},
    {"primaire": "#231942", "secondaire": "#9F86C0", "accent": "#E0B1CB"},
    {"primaire": "#03071E", "secondaire": "#D00000", "accent": "#FFBA08"},
    {"primaire": "#03045E", "secondaire": "#0077B6", "accent": "#CAF0F8"},
]

SYSTEM_PROMPT = (
    "Tu es un directeur de creation e-commerce. Reponds uniquement avec un objet JSON avec les "
    "cles : nom, slogan, palette_couleurs (objet avec primaire, secondaire, accent en hexadecimal), "
    "logo_placeholder_url."
)


def _build_brand_rules(niche_nom: str, produits: list[dict]) -> dict:
    digest = hashlib.sha256(niche_nom.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(PALETTES)
    palette = PALETTES[index]

    mot_cle = niche_nom.split()[0].capitalize() if niche_nom else "Shop"
    nom = f"{mot_cle}Store"
    slogan = f"Le meilleur de {niche_nom.lower()}, livre chez vous."

    return {
        "nom": nom,
        "slogan": slogan,
        "palette_couleurs": palette,
        "logo_placeholder_url": f"https://placehold.co/200x200?text={mot_cle}",
    }


def build_brand(niche_nom: str, produits: list[dict]) -> dict:
    noms_produits = ", ".join(p["nom"] for p in produits[:5])
    user_prompt = f"Niche : {niche_nom}\nProduits : {noms_produits}\nCree une identite de marque."
    try:
        data = ask_claude_json(SYSTEM_PROMPT, user_prompt)
        if isinstance(data, dict) and "nom" in data:
            return data
    except ClaudeUnavailableError:
        pass
    except Exception:
        pass

    return _build_brand_rules(niche_nom, produits)
