# CartePro Backend

A Flask-based backend that powers CartePro digital business cards. It provides user authentication, card CRUD, QR generation, Stripe integration, and admin operations.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Summary](#api-summary)
- [Testing](#testing)
- [Documentation](#documentation)
- [Deployment](#deployment)
- [License](#license)

## Features
- Authentication: register, login, logout, profile management.
- Card management: CRUD with per-user ownership.
- QR code generation.
- Stripe configuration + webhook handling.
- Admin endpoints for users, cards, and backups.
- Rate limiting on login.

## Architecture
- **Flask Blueprints**: `auth`, `cards`, `admin`, `stripe`, `qr`, `public`.
- **SQLAlchemy models**: `User`, `Card`, `Subscription`.
- **Utilities**: pagination helpers and QR code service.
- **Extensions**: database, login manager, rate limiter.

## Project Structure
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
```

## Getting Started
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Configuration
Environment variables (typical for production):
```
SECRET_KEY=...
DATABASE_URL=...
STRIPE_SECRET_KEY=...
STRIPE_PUBLIC_KEY=...
STRIPE_WEBHOOK_SECRET=...
```

## API Summary
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
- `GET /`
- `GET /view/<card_id>`
- `GET /health`

## Testing
```bash
pytest -q
```

## Documentation
- English: `docs/ENGINEERING_DOCUMENTATION.en.md`
- Français: `docs/ENGINEERING_DOCUMENTATION.fr.md`
- Engineering review: `docs/ENGINEERING_REVIEW.en.md` / `docs/ENGINEERING_REVIEW.fr.md`

## Deployment
- Use a WSGI server with `wsgi.py` (e.g., Gunicorn).
- Docker is supported via `Dockerfile` and `docker-compose.yml`.

## License
MIT
