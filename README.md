# 📇 CartePro Backend

**CartePro** is a secure, modular backend built with Flask for managing digital business cards, QR code generation, user authentication, and premium membership via Stripe.

---

## 🚀 Features

- 🔐 **Authentication**: Register, login, logout, and `/auth/me` to get the connected user
- 📇 **Card Management**: Full CRUD for professional cards linked to users (`/api/v1/cards`)
- � QR Code Generator: Generate branded QR codes with logo overlays
- 💳 **Stripe Integration**: Subscription handling via `/api/v1/config`, secured with environment variables
- ⚙️ **Admin Panel**: View users, cards, backups, and perform admin actions (with role protection)
- 🛠️ **Error Handling**: Custom JSON and template-based error responses (404, 500)
- ✅ **Testing**: Pytest suite covering auth, CRUD, Stripe, and protected routes
- 🔁 **CI/CD**: GitHub Actions workflow for linting, testing, and deployment

---

## 📁 Project Structure

```
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
├── instance/app.db         # SQLite DB
├── tests/                  # Pytest test suite
│   ├── test_api.py
│   ├── test_auth.py
│   └── test_stripe.py
│
├── .env                    # Environment config (not tracked)
├── requirements.txt        # Python dependencies
├── run.py                  # App entry point
└── .github/workflows/      # GitHub Actions CI
```

---

## 🛠️ Setup

```bash
# Clone the repo
git clone https://github.com/yourname/cartepro-backend
cd cartepro-backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env  # Then edit .env with your keys

# Run the app
python run.py
```

---

## 🔑 .env Configuration (example)

```
SECRET_KEY=your-secret-key
STRIPE_API_KEY=your-stripe-secret
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

- `GET /api/v1/config` — Retrieve Stripe plan info

### ⚙️ Admin (admin role only)

- `GET /admin/users` — List users
- `GET /admin/cards` — List all cards
- `GET /admin/backups` — List encrypted backups

---

## 🧪 Testing

```bash
pytest tests/
```

All tests are written using Pytest and cover auth, API CRUD, Stripe config, and protected routes.

---

## 🚀 Deployment

Project is ready for deployment to [Render](https://render.com), Railway or any other platform.

- Port is automatically bound from `os.environ["PORT"]`
- CI workflow handles testing and lint before deploy

---

## 📚 License

MIT License

