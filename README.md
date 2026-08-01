# AI Commerce Builder

Moteur IA privé permettant à Lao KENAO d'automatiser le lancement d'une activité e-commerce : recherche de niche, sélection de produits, création de marque, construction de boutique, marketing et préparation des ventes.

Ce n'est pas une plateforme SaaS : c'est un outil interne, à usage unique (un seul administrateur), qui pilote les 8 étapes du lancement d'une boutique (niche → produits → marque → boutique → vérification → import → marketing → ventes).

Voir la documentation de référence :
- `000_Project_Charter_v1.1.md`
- `001_Product_Principles_v1.1.md`
- `010_Product_Requirements_v1.1.md`
- `020_System_Architecture_v1.1.md`
- `030_Technical_Specification_v1_0.md`

## Stack

- Frontend : Streamlit
- Backend : logique métier FastAPI (`backend/api`, `backend/commerce_engine`, `backend/ai_engine`, `backend/payment_engine`, `backend/store_builder`), appelée directement en process par le frontend (voir plus bas)
- Base de données : SQLite (SQLAlchemy)
- Auth : admin unique, mot de passe hashé (bcrypt)
- Déploiement : Streamlit Community Cloud (share.streamlit.io)

## Architecture d'exécution : un seul processus

Streamlit Community Cloud ne lance qu'un seul processus Python (`frontend/app.py`) : il n'y a pas de serveur HTTP backend séparé exposé sur un port distinct.

`frontend/services.py` appelle donc **directement en Python** les fonctions déjà présentes dans `backend/api/*.py` (elles-mêmes de simples enveloppes autour du Commerce Engine, des modules IA, du Payment Engine et des requêtes SQLAlchemy), sans passer par une requête HTTP ni par le routing FastAPI.

`backend/main.py` et les modules `backend/api/*.py` restent inchangés et utilisables tels quels pour exposer une véritable API REST externe en Phase 2 : il suffira de les lancer avec un serveur ASGI (`uvicorn backend.main:app`) comme n'importe quelle API FastAPI classique, en parallèle ou à la place de ce mode d'appel direct.

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # puis renseigner les valeurs
```

## Lancer l'application

```bash
streamlit run frontend/app.py
```

Un seul processus à lancer : le backend n'est pas un service séparé, il est appelé directement en Python par les pages Streamlit via `frontend/services.py`.

## (Optionnel) Lancer le backend comme API REST autonome

Utile uniquement pour des tests d'API externes ou une future intégration SaaS (Phase 2) ; non nécessaire pour utiliser l'application Streamlit :

```bash
uvicorn backend.main:app --reload --port 8000
```

## Tests

```bash
pytest backend/tests
```

## Sécurité

Aucun secret n'est présent dans ce dépôt. Toutes les clés et identifiants doivent être renseignés dans un fichier `.env` local (voir `.env.example`), qui est ignoré par Git.

## Déploiement sur Streamlit Community Cloud (share.streamlit.io)

Streamlit Community Cloud est gratuit et conçu pour ce type d'application (un seul fichier Streamlit, un seul processus). Aucun Dockerfile, aucune configuration de conteneur n'est nécessaire.

### Étape préalable : pousser ce dépôt sur GitHub

Streamlit Community Cloud déploie à partir d'un dépôt **GitHub** (pas directement depuis votre machine). Si ce n'est pas déjà fait :

1. Créer un dépôt vide sur https://github.com/new (ne pas cocher "Initialize with README", ce dépôt en a déjà un).
2. Ajouter le remote et pousser :
   ```bash
   git remote add origin https://github.com/<votre-utilisateur>/<nom-du-depot>.git
   git push -u origin master
   ```

### Créer et configurer le Space Streamlit

1. Aller sur https://share.streamlit.io et se connecter avec votre compte GitHub.
2. Cliquer sur **New app**, puis choisir :
   - **Repository** : le dépôt GitHub poussé à l'étape précédente
   - **Branch** : `master` (ou `main` selon votre dépôt)
   - **Main file path** : `frontend/app.py`
3. Dans **Advanced settings → Secrets**, renseigner les mêmes clés que `.env.example`, au format TOML, par exemple :
   ```toml
   SECRET_KEY = "une-longue-chaine-aleatoire"
   ADMIN_EMAIL = "admin@example.com"
   ADMIN_PASSWORD = "changeme"
   ANTHROPIC_API_KEY = ""
   PAYMENT_PROVIDER_ACTIVE = "manual,yas_tmoney,moov_money,card"
   PAYMENT_SIMULATE = "true"
   CINETPAY_API_KEY = ""
   CINETPAY_SITE_ID = ""
   CINETPAY_ENABLED = "false"
   ```
   Streamlit Community Cloud expose ces secrets comme variables d'environnement au démarrage, lues automatiquement par `backend/security/secrets.py` (`pydantic-settings`).
4. Cliquer sur **Deploy**. Streamlit Community Cloud installe automatiquement `requirements.txt` (présent à la racine du dépôt) puis lance `streamlit run frontend/app.py`.
5. Activer CinetPay plus tard : modifier le secret `PAYMENT_PROVIDER_ACTIVE` pour y ajouter `cinetpay`, et renseigner `CINETPAY_API_KEY` / `CINETPAY_SITE_ID` / `CINETPAY_ENABLED = "true"`, sans modifier le code.

### Limitation connue : stockage éphémère

La base SQLite (`ai_commerce_builder.db`) est stockée dans le système de fichiers du conteneur Streamlit Community Cloud. Ce stockage **n'est pas persistant** : il est réinitialisé à chaque redémarrage de l'app (redéploiement, mise en veille après inactivité, mise à jour du dépôt). Toutes les campagnes, produits, commandes et paiements créés seront perdus à chaque redémarrage.

Pour une persistance durable en production, prévoir en Phase 2 une migration vers une base externe managée (ex. PostgreSQL sur Supabase, Neon, Railway...) en changeant simplement `DATABASE_URL` — c'est exactement pour cela que le projet utilise SQLAlchemy plutôt que SQLite en direct.
