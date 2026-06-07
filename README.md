# 📇 CartePro Backend

**CartePro** is a secure Flask backend for managing digital business cards, QR code generation, authentication, premium subscriptions with Stripe, centralized API error handling, and rate limiting.

---

## 🎯 Portfolio Overview

CartePro Backend demonstrates a production-oriented API architecture for a SaaS product. It focuses on authentication, protected resources, subscription payment workflows, QR code generation, admin tooling, automated tests, Docker support, and CI/CD readiness.

**GitHub description suggestion:**

> Secure Flask SaaS backend for digital business cards, QR codes, Stripe subscriptions, admin tooling, rate limiting, tests, Docker, and CI/CD.

**Suggested topics:**

```text
flask python sqlalchemy stripe qr-code saas rest-api authentication flask-admin docker pytest github-actions rate-limiting backend portfolio-project
```

---

## 🚀 Features

- 🔐 **Authentication**: Register, login, logout, and `/auth/me` to get the connected user
- 📇 **Card Management**: Full CRUD for professional cards linked to users (`/api/v1/cards`)
- 📎 **QR Code Generator**: Generate branded QR codes with logo overlays
- 💳 **Stripe Integration**: Subscription handling via `/api/v1/stripe/*`, secured with environment variables and webhook signature checks
- ⚙️ **Admin Panel**: View users, cards, backups, and perform admin actions with role protection
- 🛠️ **Error Handling**: Centralized API error handling with DB rollback and structured logging
- 🚦 **Rate Limiting**: Flask-Limiter with configurable Redis-backed storage for production
- ✅ **Testing**: Pytest suite covering auth, CRUD, Stripe, and protected routes
- 🔁 **CI/CD**: GitHub Actions workflow for tests, security scans, and dependency auditing

---

## 📸 Captures

> Screenshots and demo GIFs should be stored in `/screenshots`.
>
> The image links below are ready for recruiter-facing documentation once the files are generated locally and committed.

### Health endpoint

![Health endpoint](screenshots/health.png)

### API routes / backend overview

![API routes](screenshots/api-routes.png)

### Admin or backend demo

![Backend demo](screenshots/demo.gif)

Recommended files:

```text
screenshots/health.png
screenshots/api-routes.png
screenshots/admin.png
screenshots/demo.gif
```

---

## 📁 Project Structure

```text
backend/
├── app/
│   ├── __init__.py          # App factory, blueprints, extensions
│   ├── models.py            # User and Card models (SQLAlchemy)
│   ├── routes.py            # API routes (cards, QR, Stripe, admin)
│   ├── auth.py              # Auth routes
│   ├── services.py          # Utilities (QR generation, etc.)
│   ├── extensions.py        # Extensions (db, login_manager)
│   ├── admin.py             # Admin config (Flask-Admin)
│   ├── templates/errors/    # Error pages (404.html, etc.)
│   └── static/logo.png      # Logo for QR codes
│
├── instance/app.db          # SQLite DB for local development
├── tests/                   # Pytest test suite
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_stripe.py
│
├── .env                     # Environment config, not tracked
├── requirements.txt         # Python dependencies
├── run.py                   # App entry point
└── .github/workflows/       # GitHub Actions CI
```

---

## 🛠️ Local Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Default local URL:

```text
http://localhost:5000
```

---

## 🔑 Environment Configuration

Example `.env`:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+psycopg2://cartepro:cartepro@db:5432/cartepro
RATELIMIT_STORAGE_URI=redis://redis:6379/0
CORS_ORIGINS=http://localhost:3000
STRIPE_SECRET_KEY=your-stripe-secret
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

---

## ✅ API Endpoints Summary

### 🔐 Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `PATCH /auth/me` — Update profile
- `DELETE /auth/me` — Delete account
- `POST /auth/avatar` — Upload avatar

### 📇 Cards

- `POST /api/v1/cards` — Create
- `GET /api/v1/cards/<id>` — Read
- `PUT /api/v1/cards/<id>` — Update
- `DELETE /api/v1/cards/<id>` — Delete

### 📎 QR Code

- `POST /generate_qr` — Generate QR with logo

### Misc

- `GET /health` — Health check

### 💳 Stripe

- `GET /api/v1/stripe/config` — Retrieve Stripe plan info
- `POST /api/v1/stripe/webhook` — Receive Stripe webhook events

### ⚙️ Admin

- `GET /api/v1/admin/users` — List users
- `GET /api/v1/admin/cards` — List all cards
- `GET /api/v1/admin/backups` — List encrypted backups

---

## 🧪 Testing

```bash
pytest tests/
```

The test suite covers authentication, protected routes, card CRUD, Stripe configuration, and API behavior.

---

## 🎥 Capture Workflow

Create the screenshots folder:

```bash
mkdir -p screenshots
```

Start the backend:

```bash
python run.py
```

Suggested screenshots:

```text
http://localhost:5000/health
http://localhost:5000/admin
```

Create a 20-30 second GIF using a local screen recording and FFmpeg:

```bash
ffmpeg -i demo.mov -vf "fps=12,scale=1280:-1:flags=lanczos" screenshots/demo.gif
```

---

## 🚀 Deployment

Project is ready for deployment to Render, Railway, or another container-friendly platform.

- Port is automatically bound from `os.environ["PORT"]`
- `render.yaml` provisions the web service, Postgres database, and Redis for persistent rate limiting
- CI workflow runs tests, Bandit, dependency auditing, and blocking lint checks for real failures

Run locally with Docker:

```bash
docker-compose up --build
```

---

## 📚 License

MIT License
