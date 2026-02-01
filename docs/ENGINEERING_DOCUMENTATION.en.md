# CartePro Backend Engineering Documentation (EN)

## 1. Scope
This document describes how the CartePro backend is structured, how major components interact, and how to operate the service in local, test, and production environments.

## 2. System Overview
CartePro is a Flask application that provides:
- Authentication and profile management.
- CRUD operations for digital business cards.
- QR code generation for cards.
- Stripe billing configuration and webhook processing.
- Admin endpoints for user, card, and backup management.

## 3. Architecture & Runtime Flow
```
Client -> Flask Blueprints -> Services/Models -> Database
                         -> External services (Stripe)
```
- **Flask Blueprints** define route boundaries (`auth`, `cards`, `admin`, `stripe`, `qr`, `public`).
- **Models** (SQLAlchemy) store users, cards, and subscriptions.
- **Utilities** provide pagination helpers and QR generation.
- **Extensions** centralize shared infrastructure (DB, login manager, rate limiter).

## 4. Project Structure
```
app/
  __init__.py          # App factory + blueprint registration
  auth.py              # Auth routes
  models.py            # SQLAlchemy models
  services.py          # QR service
  utils.py             # Pagination helpers
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
config.py              # Environment configuration
run.py                 # Local run entry point
wsgi.py                # WSGI entry point
manage.py              # CLI helper (if used)
```

## 5. Data Model
- **User**: credentials, role, admin flag, Stripe customer id, avatar, derived subscription status.
- **Card**: UUID primary key, owner user_id, contact fields, plan metadata, delete flag.
- **Subscription**: Stripe subscription metadata tied to a user.

## 6. API Surface (by Blueprint)
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
- `Config` classes live in `config.py` and select based on `FLASK_ENV`.
- Required environment variables for production:
  - `SECRET_KEY`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_PUBLIC_KEY`
  - `DATABASE_URL`

## 8. Security & AuthZ
- **Flask-Login** manages sessions.
- **Admin authorization** is enforced by `admin_required` decorator.
- Rate limiting is enabled for login (`5/min`).

## 9. Testing Strategy
- Tests live under `tests/` and are executed with `pytest`.
- Coverage today focuses on auth, cards CRUD, and admin routes.

## 10. Deployment
- Use `wsgi.py` with a WSGI server (Gunicorn/Uvicorn). 
- Docker support is available via `Dockerfile` and `docker-compose.yml`.

## 11. Observability & Logging
- Loguru writes logs to `instance/app.log`.
- Standard Flask error handlers render 404/500 templates.

## 12. Known Gaps & Follow-ups
See `docs/ENGINEERING_REVIEW.en.md` for detailed technical debt and missing test coverage.
