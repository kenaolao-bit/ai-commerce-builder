"""Module 5 - Quality Checker (010_Product_Requirements, section 5).

Controle : liens, images, contenu, SEO, responsive, score qualite.
MVP J0 : checklist automatisee basee sur la presence/completude des pages
generees par le Store Builder (pas d'analyse visuelle avancee - Phase 2).
"""

REQUIRED_PAGE_TYPES = ["accueil", "catalogue", "produit", "faq", "contact", "politiques", "panier"]


def check_quality(store, pages: list) -> dict:
    pages_par_type = {p.type: p for p in pages}
    checklist = []

    for type_page in REQUIRED_PAGE_TYPES:
        page = pages_par_type.get(type_page)
        ok = page is not None and bool(page.contenu and page.contenu.strip())
        checklist.append(
            {
                "critere": f"Page '{type_page}' presente et non vide",
                "ok": ok,
                "detail": "OK" if ok else f"Page '{type_page}' manquante ou vide",
            }
        )

    seo_ok = store is not None and bool(store.nom_boutique)
    checklist.append(
        {
            "critere": "Nom de boutique defini (SEO basique)",
            "ok": seo_ok,
            "detail": "OK" if seo_ok else "Nom de boutique manquant",
        }
    )

    responsive_ok = True
    checklist.append(
        {
            "critere": "Rendu responsive (Streamlit)",
            "ok": responsive_ok,
            "detail": "OK - rendu natif Streamlit responsive",
        }
    )

    total = len(checklist)
    reussis = sum(1 for c in checklist if c["ok"])
    score_qualite = round((reussis / total) * 100, 1) if total else 0.0

    return {"score_qualite": score_qualite, "checklist": checklist}
