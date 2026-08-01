---
title: AI Commerce Builder
emoji: 🛒
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# AI Commerce Builder

Moteur IA privé permettant à Lao KENAO d'automatiser le lancement d'une activité e-commerce : recherche de niche, sélection de produits, création de marque, construction de boutique, marketing et préparation des ventes.

Voir la documentation de référence :
- `000_Project_Charter_v1.1.md`
- `001_Product_Principles_v1.1.md`
- `010_Product_Requirements_v1.1.md`
- `020_System_Architecture_v1.1.md`
- `030_Technical_Specification_v1_0.md`

## Stack

- Frontend : Streamlit
- Backend : FastAPI
- Base de données : SQLite (SQLAlchemy)
- Auth : JWT
- Déploiement : Hugging Face Spaces

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # puis renseigner les valeurs
```

## Lancer le backend

```bash
uvicorn backend.main:app --reload --port 8000
```

## Lancer le frontend

```bash
streamlit run frontend/app.py
```

## Tests

```bash
pytest backend/tests
```

## Sécurité

Aucun secret n'est présent dans ce dépôt. Toutes les clés et identifiants doivent être renseignés dans un fichier `.env` local (voir `.env.example`), qui est ignoré par Git.

## Déploiement sur Hugging Face Spaces

Le Space utilise le SDK **Docker** (`sdk: docker` ci-dessus) : un seul conteneur
exécute a la fois le backend FastAPI (port interne 8000) et le frontend
Streamlit (port 7860, expose par le Space), via `start.sh`.

1. Créer un Space sur https://huggingface.co/new-space avec le SDK **Docker**.
2. Lier ce dépôt GitHub au Space (ou pousser directement dessus).
3. Dans **Settings → Repository secrets** du Space, renseigner les mêmes clés
   que `.env.example` (`SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`,
   `ANTHROPIC_API_KEY`, `CINETPAY_*`, etc.) — jamais dans le code ni dans `README.md`.
4. Le Space build automatiquement l'image à partir du `Dockerfile` et démarre
   `start.sh` au déploiement.
5. Activer CinetPay plus tard : ajouter `cinetpay` à `PAYMENT_PROVIDER_ACTIVE`
   et renseigner `CINETPAY_API_KEY` / `CINETPAY_SITE_ID` /
   `CINETPAY_ENABLED=true` dans les secrets du Space, sans modifier le code.
