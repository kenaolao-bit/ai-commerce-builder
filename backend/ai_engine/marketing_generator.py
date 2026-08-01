"""Module 6 - Marketing Generator (010_Product_Requirements, section 5).

Produit automatiquement : publications Facebook, Instagram, TikTok, emails,
descriptions SEO.
"""

from backend.ai_engine._claude_client import ClaudeUnavailableError, ask_claude_json

SYSTEM_PROMPT = (
    "Tu es un community manager e-commerce. Reponds uniquement avec un tableau JSON d'objets, "
    "chacun avec les cles : type (facebook/instagram/tiktok/email/seo) et contenu (texte pret a "
    "publier)."
)


def _generate_marketing_rules(brand: dict, produits: list[dict]) -> list[dict]:
    nom_marque = brand.get("nom", "Notre boutique")
    slogan = brand.get("slogan", "")
    premier_produit = produits[0]["nom"] if produits else "nos produits"

    return [
        {
            "type": "facebook",
            "contenu": (
                f"{nom_marque} est en ligne ! Decouvrez {premier_produit} et toute notre "
                f"gamme. {slogan} Commandez des maintenant."
            ),
        },
        {
            "type": "instagram",
            "contenu": (
                f"✨ {nom_marque} ✨\n{slogan}\nDecouvrez {premier_produit} en lien dans la bio."
                f"\n#ecommerce #Togo #{nom_marque.replace(' ', '')}"
            ),
        },
        {
            "type": "tiktok",
            "contenu": (
                f"On vous presente {premier_produit} par {nom_marque}. {slogan} "
                "Regardez jusqu'au bout pour l'offre de lancement !"
            ),
        },
        {
            "type": "email",
            "contenu": (
                f"Objet : {nom_marque} ouvre sa boutique en ligne\n\nBonjour,\n\n{nom_marque} "
                f"vous presente {premier_produit} et toute sa gamme. {slogan}\n\nDecouvrez la "
                "boutique des aujourd'hui.\n\nA bientot,\nL'equipe " + nom_marque
            ),
        },
        {
            "type": "seo",
            "contenu": (
                f"{nom_marque} - {slogan} Achetez {premier_produit} et bien plus en ligne, "
                "livraison rapide au Togo."
            ),
        },
    ]


def generate_marketing(brand: dict, produits: list[dict]) -> list[dict]:
    noms_produits = ", ".join(p["nom"] for p in produits[:5])
    user_prompt = (
        f"Marque : {brand.get('nom')}\nSlogan : {brand.get('slogan')}\n"
        f"Produits : {noms_produits}\nGenere les contenus marketing de lancement."
    )
    try:
        data = ask_claude_json(SYSTEM_PROMPT, user_prompt)
        if isinstance(data, list) and data:
            return data
    except ClaudeUnavailableError:
        pass
    except Exception:
        pass

    return _generate_marketing_rules(brand, produits)
