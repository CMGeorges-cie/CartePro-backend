# config.py
import os

class Config:
    """Configuration de base de l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/cards.db'
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
