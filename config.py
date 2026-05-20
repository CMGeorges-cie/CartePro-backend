# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cards.db")


class Config:
    """Configuration de base."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{DEFAULT_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    ENV_NAME = os.environ.get('FLASK_ENV', 'development')
    CORS_ORIGINS = [
        o.strip() for o in os.environ.get('CORS_ORIGINS', '*').split(',') if o.strip()
    ]
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_MONTHLY_PRICE_ID = os.environ.get('STRIPE_MONTHLY_PRICE_ID')
    STRIPE_ANNUAL_PRICE_ID = os.environ.get('STRIPE_ANNUAL_PRICE_ID')

    # Email (SendGrid)
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@cartepro.ca')

    # URL du frontend (redirections Stripe)
    APP_URL = os.environ.get('APP_URL', 'http://localhost:3000')

    # Stockage fichiers — S3 / Cloudflare R2 / local
    # Laisser S3_BUCKET vide pour utiliser le stockage disque local.
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')  # R2 : https://<acct>.r2.cloudflarestorage.com


class DevelopmentConfig(Config):
    SECRET_KEY = Config.SECRET_KEY or 'dev-secret-key'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = Config.SECRET_KEY or 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_STORAGE_URI = 'memory://'
    SENDGRID_API_KEY = None      # Pas d'email réel en test
    FROM_EMAIL = 'test@cartepro.ca'
    APP_URL = 'http://localhost:3000'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/0')
