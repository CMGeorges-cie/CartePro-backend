# Guide de déploiement et de tests — CartePro Pro

## 1. Déploiement sur Render

### Pré-requis
1. Compte Render (render.com)
2. Repo GitHub connecté
3. Variables d'environnement renseignées dans le dashboard Render

### Étapes

**a) Créer les services via Blueprint**
```
Dashboard Render → New → Blueprint → sélectionner ce repo
```
Le fichier `render.yaml` définit automatiquement :
- `cartepro-api` (web service Python)
- `cartepro-redis` (Redis pour rate limiting)
- `cartepro-db` (PostgreSQL 15)

**b) Variables à configurer manuellement dans Render Dashboard**

| Variable | Valeur |
|----------|--------|
| `STRIPE_SECRET_KEY` | `sk_live_...` (Stripe Dashboard) |
| `STRIPE_PUBLIC_KEY` | `pk_live_...` (Stripe Dashboard) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` (Webhooks → Add endpoint) |
| `SENDGRID_API_KEY` | Votre clé SendGrid |
| `S3_BUCKET` | Nom de votre bucket R2/S3 (optionnel) |
| `S3_ACCESS_KEY` | Clé d'accès R2/S3 (optionnel) |
| `S3_SECRET_KEY` | Secret R2/S3 (optionnel) |
| `S3_ENDPOINT_URL` | `https://<id>.r2.cloudflarestorage.com` (Cloudflare R2) |

> Les prix Stripe sont déjà dans `render.yaml` :
> - Mensuel : `price_1TdFjaGcAveCBBuL7PqcEY0j` — 15 $ CAD/mois
> - Annuel : `price_1TdFjaGcAveCBBuLuH4Kn0Yz` — 120 $ CAD/an

**c) Initialiser la base de données (première fois)**
```bash
# Dans Render Shell ou via la CLI Render :
flask db upgrade          # crée toutes les tables via Alembic
flask seed-admin          # crée le compte administrateur
```

**d) Configurer le webhook Stripe**
- URL : `https://cartepro-api.onrender.com/stripe/webhook`
- Événements : `checkout.session.completed`, `customer.subscription.deleted`

---

## 2. Tests locaux — Backend Flask

### Installation
```bash
cd CartePro-backend
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos vraies clés
```

### Lancer en développement
```bash
flask run
# ou avec Docker :
docker-compose up
```

### Lancer les tests automatisés
```bash
python3 -m pytest tests/ -v
# Résultat attendu : 63 passed
```

### Tests par module
```bash
pytest tests/test_auth.py -v        # Auth (12 tests)
pytest tests/test_api.py -v         # API générale (10 tests)
pytest tests/test_crm.py -v         # CRM (23 tests)
pytest tests/test_pro_features.py -v # Fonctions Pro (17 tests)
pytest tests/test_admin.py -v       # Admin (1 test)
```

---

## 3. Tests manuels — Postman / Insomnia

### Import de la collection
```
Postman → Import → Fichier → docs/api_collection.json
```

### Séquence de test recommandée

#### Test A — Inscription et carte
1. `POST /auth/register` — créer un compte test
2. `POST /auth/login` — se connecter
3. `GET /auth/me` — vérifier le profil
4. `POST /api/v1/cards/` — créer une carte
5. Copier l'`id` retourné → mettre dans la variable `cardId`
6. `GET /api/v1/cards/{{cardId}}/qr` — vérifier le QR code
7. `GET /public/view/{{cardId}}` — vue publique (sans auth)

#### Test B — Soumission → Contact CRM
1. `POST /api/v1/cards/{{cardId}}/quote` — simuler une demande client
2. Copier l'`id` de la soumission
3. `POST /api/v1/crm/contacts/from-quote/<id>` — convertir en contact
4. `GET /api/v1/crm/dashboard` — vérifier les stats

#### Test C — Pipeline CRM complet
1. `POST /api/v1/crm/contacts` — créer 3 contacts
2. `GET /api/v1/crm/pipeline` — vue kanban
3. `PATCH /api/v1/crm/contacts/{{contactId}}/stage` avec `"stage": "contacted"`
4. `POST /api/v1/crm/contacts/{{contactId}}/notes` — ajouter une note
5. `POST /api/v1/crm/tasks` — créer une tâche liée au contact
6. `PATCH /api/v1/crm/tasks/{{taskId}}/done` — marquer comme faite

#### Test D — Import CSV
Créer un fichier `contacts_test.csv` :
```csv
prénom,nom,courriel,téléphone,entreprise,ville
Jean,Tremblay,jean@test.com,514-555-0001,Rénovations JT,Montréal
Marie,Côté,marie@test.com,450-555-0002,Résidences MC,Laval
```
Puis : `POST /api/v1/crm/contacts/import` avec ce fichier.

#### Test E — Stripe (mode test)
1. `GET /stripe/config` — vérifier les price IDs
2. `POST /stripe/create-checkout` avec `{"plan": "monthly"}`
3. Ouvrir le `checkout_url` dans un navigateur
4. Payer avec la carte test Stripe : `4242 4242 4242 4242`

---

## 4. Application mobile Flutter

### Pré-requis
- Flutter SDK 3.19+ (`flutter --version`)
- Android Studio ou Xcode

### Configuration
```bash
cd mobile
# Éditer lib/config/api_config.dart
# Changer baseUrl selon votre environnement
flutter pub get
```

### Lancer sur émulateur/appareil
```bash
flutter run                    # appareil connecté ou émulateur par défaut
flutter run -d chrome          # Web (dev seulement)
flutter run -d <device-id>     # appareil spécifique
```

### Build de production
```bash
# Android APK
flutter build apk --release

# Android App Bundle (Play Store)
flutter build appbundle --release

# iOS (Mac seulement)
flutter build ios --release
```

### Fichier de config API (`lib/config/api_config.dart`)
```dart
// Développement local
static const String baseUrl = 'http://10.0.2.2:5000'; // émulateur Android
static const String baseUrl = 'http://localhost:5000'; // iOS simulateur

// Production
static const String baseUrl = 'https://cartepro-api.onrender.com';
```

---

## 5. Migrations de base de données

### Première installation
```bash
flask db upgrade        # applique toutes les migrations
flask seed-admin        # crée l'administrateur
```

### Après une modification de modèle
```bash
flask db migrate -m "description du changement"
flask db upgrade
```

### Rollback
```bash
flask db downgrade      # revient à la migration précédente
flask db downgrade base # revient à zéro
```

---

## 6. Administration

### Accès au panel admin
URL : `https://votre-domaine.com/admin`

Connexion avec le compte créé via `flask seed-admin`.

Fonctionnalités :
- Gestion des utilisateurs
- Voir/modifier toutes les cartes
- Voir les abonnements Stripe

---

## 7. Variables d'environnement — Référence complète

```env
# Base
SECRET_KEY=<chaîne aléatoire longue>
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/cartepro
FLASK_ENV=production

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_MONTHLY_PRICE_ID=price_1TdFjaGcAveCBBuL7PqcEY0j
STRIPE_ANNUAL_PRICE_ID=price_1TdFjaGcAveCBBuLuH4Kn0Yz

# Email (SendGrid)
SENDGRID_API_KEY=SG....
FROM_EMAIL=noreply@cartepro.ca

# App
APP_URL=https://cartepro.ca
CORS_ORIGINS=https://cartepro.ca

# Redis (rate limiting)
RATELIMIT_STORAGE_URI=redis://redis:6379/0

# Stockage S3 / Cloudflare R2 (optionnel)
S3_BUCKET=cartepro-photos
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_REGION=auto
S3_ENDPOINT_URL=https://<id>.r2.cloudflarestorage.com

# Admin
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@cartepro.ca
ADMIN_PASSWORD=<mot-de-passe-fort>
```
