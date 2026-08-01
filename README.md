---
title: AI Commerce Builder
emoji: 🛒
colorFrom: indigo
colorTo: green
sdk: streamlit
sdk_version: "1.38.0"
app_file: frontend/app.py
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
