# config.py
import os

class Config:
    """Configuration de base de l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/cards.db'
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') # Fais de même pour le secret du webhook !
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True #if os.environ.get('FLASK_ENV') == 'development' else False
    