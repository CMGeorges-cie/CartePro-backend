# Documentation d’ingénierie CartePro (FR)

## 1. Portée
Ce document décrit la structure du backend CartePro, les composants principaux, et la manière d’exécuter le service en local, test et production.

## 2. Vue d’ensemble
CartePro est une application Flask qui fournit :
- Authentification et gestion du profil.
- CRUD des cartes de visite numériques.
- Génération de QR codes.
- Configuration Stripe et traitement des webhooks.
- Endpoints d’administration pour les utilisateurs, cartes et backups.

## 3. Architecture & Flux d’exécution
```
Client -> Flask Blueprints -> Services/Models -> Base de données
                         -> Services externes (Stripe)
```
- **Blueprints Flask** : séparation des routes (`auth`, `cards`, `admin`, `stripe`, `qr`, `public`).
- **Modèles** : User, Card, Subscription via SQLAlchemy.
- **Utilities** : pagination et helpers.
- **Extensions** : DB, login manager, rate limiter.

## 4. Structure du projet
```
app/
  __init__.py          # Factory + enregistrement des blueprints
  auth.py              # Routes d’authentification
  models.py            # Modèles SQLAlchemy
  services.py          # Service QR
  utils.py             # Pagination
  extensions.py        # db, login_manager, limiter
  routes/
    admin.py
    cards.py
    qr.py
    stripe.py
    public.py
  templates/
    index.html
    card_templates.html
config.py              # Configuration
run.py                 # Lancement local
wsgi.py                # Entrée WSGI
manage.py              # CLI (si utilisé)
```

## 5. Modèle de données
- **User** : identifiants, rôle, admin, Stripe customer id, avatar, statut d’abonnement.
- **Card** : UUID, user_id, champs de contact, plan, indicateur de suppression.
- **Subscription** : métadonnées Stripe liées à un utilisateur.

## 6. API (par blueprint)
### Auth (`/auth`)
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `PATCH /auth/me`
- `DELETE /auth/me`
- `POST /auth/avatar`

### Cards (`/api/v1/cards`)
- `GET /api/v1/cards/`
- `POST /api/v1/cards/`
- `GET /api/v1/cards/<card_id>`
- `PUT /api/v1/cards/<card_id>`
- `DELETE /api/v1/cards/<card_id>`

### QR (`/api/v1/qr`)
- `POST /api/v1/qr/generate`

### Stripe (`/api/v1/stripe`)
- `GET /api/v1/stripe/config`
- `POST /api/v1/stripe/webhook`

### Admin (`/api/v1/admin`)
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/cards`
- `GET /api/v1/admin/backups`
- `POST /api/v1/admin/restore/<filename>`
- `POST /api/v1/admin/restore_card/<card_id>`
- `GET /api/v1/admin/export?model=users|cards&format=json|csv`

### Public
- `GET /` (HTML)
- `GET /view/<card_id>` (HTML)
- `GET /health`

## 7. Configuration & Secrets
- Les classes de configuration sont dans `config.py` et choisies via `FLASK_ENV`.
- Variables essentielles en production :
  - `SECRET_KEY`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_PUBLIC_KEY`
  - `DATABASE_URL`

## 8. Sécurité & Autorisations
- **Flask-Login** gère les sessions.
- **Admin authorization** via le décorateur `admin_required`.
- Rate limiting activé sur login (`5/min`).

## 9. Tests
- Les tests sont dans `tests/` et s’exécutent via `pytest`.
- La couverture actuelle vise l’auth, le CRUD cartes et les routes admin.

## 10. Déploiement
- Utiliser `wsgi.py` avec un serveur WSGI (Gunicorn/Uvicorn). 
- Docker est supporté via `Dockerfile` et `docker-compose.yml`.

## 11. Observabilité & Logs
- Loguru écrit dans `instance/app.log`.
- Handlers 404/500 via templates.

## 12. Points d’amélioration
Voir `docs/ENGINEERING_REVIEW.fr.md` pour la dette technique et les tests manquants.
