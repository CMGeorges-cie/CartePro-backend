# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# The instance folder is created by Flask when ``instance_relative_config`` is
# enabled in ``create_app``. Place the default SQLite database inside this
# folder so the path matches ``app.instance_path``.
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cards.db")

class Config:
    """Configuration de base de l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{DEFAULT_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True if os.environ.get('FLASK_ENV') == 'development' else False
    ENV_NAME = os.environ.get('FLASK_ENV', 'development')
    CORS_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ORIGINS', '*').split(',') if origin.strip()]
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    
    #Stripe settings
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') # Fais de même pour le secret du webhook !
    

class DevelopmentConfig(Config):
    """🔧 Configuration pour le développement"""
    SECRET_KEY = Config.SECRET_KEY or 'dev-secret-key'
    DEBUG = True


class TestingConfig(Config):
    """🧪 Configuration pour les tests"""
    TESTING = True
    SECRET_KEY = Config.SECRET_KEY or "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # utile si tu fais des tests avec Flask-WTF
    RATELIMIT_STORAGE_URI = "memory://"


class ProductionConfig(Config):
    """🚀 Configuration pour la production"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "redis://localhost:6379/0")
