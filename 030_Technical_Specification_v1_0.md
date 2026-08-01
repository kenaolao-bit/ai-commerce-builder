# 030_Technical_Specification.md

# AI Commerce Builder
## Spécification Technique — Version 1.0
**Statut :** Document d'implémentation pour Claude Code
**Base :** Charter v1.1, Product Principles v1.1, PRD v1.1, System Architecture v1.1

---

# 1. Objectif de ce document

Ce document traduit le PRD et l'Architecture v1.1 en spécification exploitable directement par Claude Code pour produire un MVP livrable **le jour même**.

Portée du jour J : un squelette complet et fonctionnel des 8 étapes, avec logique IA simplifiée (règles + prompts Claude) plutôt que des intégrations externes lourdes, conformément au Principe 5 (MVP avant perfection).

---

# 2. Stack technique

| Couche | Techno |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Base de données | SQLite (via SQLAlchemy, pour migration facile vers PostgreSQL) |
| Auth | JWT |
| Déploiement | Hugging Face Spaces |
| Versionning | GitHub |

---

# 3. Arborescence du projet

```
ai-commerce-builder/
├── backend/
│   ├── main.py                     # point d'entrée FastAPI
│   ├── database.py                 # connexion + session SQLAlchemy
│   ├── models/
│   │   ├── campaign.py
│   │   ├── niche.py
│   │   ├── product.py
│   │   ├── brand.py
│   │   ├── store.py
│   │   ├── order.py
│   │   └── payment.py
│   ├── schemas/                    # Pydantic (validation API)
│   ├── api/
│   │   ├── campaigns.py
│   │   ├── niches.py
│   │   ├── products.py
│   │   ├── brand.py
│   │   ├── store.py
│   │   ├── quality.py
│   │   ├── marketing.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── dashboard.py
│   ├── ai_engine/
│   │   ├── niche_finder.py
│   │   ├── product_finder.py
│   │   ├── brand_builder.py
│   │   ├── quality_checker.py
│   │   └── marketing_generator.py
│   ├── commerce_engine/
│   │   ├── engine.py                # orchestrateur des 8 étapes
│   │   └── steps.py
│   ├── store_builder/
│   │   └── builder.py
│   ├── payment_engine/
│   │   ├── base.py                  # interface PaymentProvider
│   │   ├── engine.py                # orchestrateur, sélection du provider
│   │   └── providers/
│   │       ├── yas_tmoney.py
│   │       ├── moov_money.py
│   │       ├── card_provider.py
│   │       └── cinetpay.py          # ajouté plus tard, non actif au J0
│   ├── security/
│   │   ├── auth.py                  # JWT
│   │   └── secrets.py               # lecture .env
│   └── tests/
├── frontend/
│   ├── app.py                       # entrée Streamlit
│   ├── pages/
│   │   ├── 1_Dashboard_CEO.py
│   │   ├── 2_Nouvelle_Campagne.py
│   │   ├── 3_Niches.py
│   │   ├── 4_Produits.py
│   │   ├── 5_Marque.py
│   │   ├── 6_Boutique.py
│   │   ├── 7_Marketing.py
│   │   └── 8_Commandes.py
│   └── components/
├── .env.example
├── requirements.txt
└── README.md
```

---

# 4. Base de données (schéma MVP — SQLite)

## Table `campaigns`
- id, nom, pays_cible, langue, budget, objectif, statut, étape_courante (1-8), date_création

## Table `niches`
- id, campaign_id, nom, score_opportunité, niveau_concurrence, recommandation, statut (proposée/retenue)

## Table `products`
- id, campaign_id, nom, fournisseur, prix_fournisseur, prix_conseillé, marge_estimée, statut (proposé/importé)

## Table `brands`
- id, campaign_id, nom, slogan, palette_couleurs (json), logo_placeholder_url

## Table `stores`
- id, campaign_id, nom_boutique, url, statut (brouillon/publiée), score_qualité

## Table `store_pages`
- id, store_id, type (accueil/catalogue/produit/faq/contact/politiques/panier), contenu

## Table `marketing_assets`
- id, campaign_id, type (facebook/instagram/tiktok/email/seo), contenu, statut

## Table `orders`
- id, store_id, client_nom, client_contact, montant, statut, date

## Table `payments`
- id, order_id, provider (yas_tmoney/moov_money/card/cinetpay), transaction_ref, statut, montant, devise, date

## Table `users`
- id, email, mot_de_passe_hash, rôle (admin), date_création

---

# 5. Commerce Engine — orchestrateur des 8 étapes

Le Commerce Engine pilote une machine à états simple par campagne :

```
1. NICHE_RECHERCHE      → Niche Finder
2. BOUTIQUE_INIT        → Store Builder (structure vide)
3. PRODUITS_RECHERCHE   → Product Finder
4. MARQUE_CREATION      → Brand Builder
5. BOUTIQUE_VERIFICATION→ Quality Checker
6. PRODUITS_IMPORT      → Store Builder (injection produits + marque)
7. MARKETING_PREPARATION→ Marketing Generator
8. VENTES_PREPARATION   → Commerce Engine (publication + activation Payment Engine)
```

Chaque étape :
- lit l'état de la campagne en base ;
- exécute le module IA correspondant ;
- écrit le résultat en base ;
- fait avancer `étape_courante` ;
- expose son statut au Dashboard CEO.

Endpoint clé : `POST /campaigns/{id}/advance` → exécute l'étape suivante et retourne le résultat.

---

# 6. Modules IA (logique simplifiée pour le MVP du jour)

Pour tenir le délai, chaque module IA du jour J utilise soit des règles déterministes, soit un appel à l'API Claude avec un prompt structuré retournant du JSON — sans dépendances externes lourdes (pas de scraping fournisseur en direct, pas d'API tierces non validées).

| Module | Entrée | Sortie J0 (MVP) | Évolution Phase 2 |
|---|---|---|---|
| Niche Finder | pays, langue, budget, objectif | 3-5 niches scorées via prompt Claude structuré | Données marché réelles (Google Trends, etc.) |
| Product Finder | niche retenue | 5-10 produits avec marge estimée (génération assistée) | Scraping fournisseurs réels (AliExpress etc., hors périmètre MVP) |
| Brand Builder | niche + produits | nom, slogan, palette, logo placeholder | Génération logo IA réelle |
| Quality Checker | boutique générée | checklist automatisée (liens, champs requis, SEO basique) | Analyse visuelle avancée |
| Marketing Generator | marque + produits | posts FB/IG/TikTok, email, description SEO | Programmation/publication automatique |

---

# 7. Store Builder

Génère les pages `store_pages` (accueil, catalogue, fiche produit, FAQ, contact, politiques, panier) à partir de templates Streamlit/HTML paramétrés par la marque et les produits de la campagne.

MVP jour J : rendu Streamlit multi-pages consultable en interne (pas de boutique publique séparée) — suffisant pour valider le flux et démontrer le produit.

---

# 8. Payment Engine (déjà validé)

## Interface commune

```python
class PaymentProvider(ABC):
    @abstractmethod
    def initiate_payment(self, order_id: str, amount: float, currency: str, customer: dict) -> PaymentResult: ...

    @abstractmethod
    def check_status(self, transaction_ref: str) -> PaymentStatus: ...

    @abstractmethod
    def handle_webhook(self, payload: dict) -> PaymentEvent: ...
```

## Règles
- Le Commerce Engine ne parle qu'à `PaymentEngine`, jamais à un provider directement.
- Chaque provider (`YASTMoneyProvider`, `MoovMoneyProvider`, `CardProvider`) est un module isolé, activable/désactivable par configuration (`.env` : `PAYMENT_PROVIDER_ACTIVE=yas_tmoney,moov_money`).
- Mode `simulate=True` par défaut au J0 : génère des transactions fictives cohérentes (statut, référence, délai simulé) pour tester tout le flux de vente sans compte marchand validé.
- `CinetPayProvider` : fichier présent dans `providers/`, non activé, prêt à brancher dès validation du compte (ajout d'une ligne de config, aucune modification ailleurs).
- Statuts normalisés en interne : `pending`, `success`, `failed`.

---

# 9. API REST — endpoints principaux

```
POST   /campaigns                     Créer une campagne
GET    /campaigns/{id}                Détail + étape courante
POST   /campaigns/{id}/advance        Exécuter l'étape suivante

GET    /campaigns/{id}/niches
POST   /campaigns/{id}/niches/select

GET    /campaigns/{id}/products
POST   /campaigns/{id}/products/import

GET    /campaigns/{id}/brand

GET    /campaigns/{id}/store
GET    /campaigns/{id}/store/quality

GET    /campaigns/{id}/marketing

POST   /orders
GET    /orders/{id}

POST   /payments/initiate
POST   /payments/webhook/{provider}
GET    /payments/{id}/status

GET    /dashboard/kpis
```

---

# 10. Dashboard CEO

`GET /dashboard/kpis` retourne :
- chiffre d'affaires total
- nombre de ventes / commandes
- produits actifs
- campagnes en cours + progression (étape X/8)
- alertes (ex : étape bloquée, paiement en échec)

Page Streamlit correspondante : `1_Dashboard_CEO.py`, rafraîchissement à la demande.

---

# 11. Sécurité

- JWT pour l'authentification admin (utilisateur unique au MVP : Lao KENAO).
- Mots de passe hashés (bcrypt).
- Secrets (clés API Claude, futurs identifiants CinetPay) dans `.env`, jamais commités (`.gitignore` dès l'initialisation du repo).
- Journalisation basique des actions sensibles (paiement, publication).

---

# 12. Plan d'exécution pour Claude Code (aujourd'hui)

**Ordre d'implémentation recommandé :**

1. Initialiser le repo, `requirements.txt`, `.env.example`, structure de dossiers.
2. Backend : `database.py`, modèles SQLAlchemy, migrations initiales.
3. Payment Engine (interface + providers stub + mode simulate) — car il structure tout le flux de commande.
4. Commerce Engine (machine à états des 8 étapes) + endpoints `campaigns`.
5. Modules IA un par un (Niche → Product → Brand → Quality → Marketing), chacun testable isolément via son endpoint.
6. Store Builder (génération des pages).
7. Dashboard CEO (endpoint + page Streamlit).
8. Frontend Streamlit : pages dans l'ordre du flux métier.
9. Tests unitaires de base sur Commerce Engine et Payment Engine.
10. Déploiement sur Hugging Face Spaces.

---

# 13. Définition du "Done" pour le MVP du jour

- [ ] Une campagne peut être créée et parcourir les 8 étapes sans erreur.
- [ ] Chaque module IA retourne un résultat exploitable (même simplifié).
- [ ] Une boutique est visible avec ses pages générées.
- [ ] Une commande peut être créée et un paiement simulé peut être initié et confirmé.
- [ ] Le Dashboard CEO affiche les indicateurs à jour.
- [ ] Le Payment Engine est prêt à recevoir CinetPay sans modification du reste du code.
- [ ] Aucun secret n'est présent dans le dépôt Git.
