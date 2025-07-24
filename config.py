# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# The instance folder is created by Flask when ``instance_relative_config`` is
# enabled in ``create_app``. Place the default SQLite database inside this
# folder so the path matches ``app.instance_path``.
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cards.db")

class Config:
    """Configuration de base de l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{DEFAULT_DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True if os.environ.get('FLASK_ENV') == 'development' else False
    
    #Stripe settings
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') # Fais de même pour le secret du webhook !
    

class DevelopmentConfig(Config):
    """🔧 Configuration pour le développement"""
    
    DEBUG = True


class TestingConfig(Config):
    """🧪 Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # utile si tu fais des tests avec Flask-WTF


class ProductionConfig(Config):
    """🚀 Configuration pour la production"""
    DEBUG = False
    TESTING = False
    # Possibilité d'ajouter des règles de sécurité ou de log ici
