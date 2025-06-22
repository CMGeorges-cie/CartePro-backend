# app/models.py

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# On crée l'instance de la base de données qui sera utilisée partout
db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    # Relation (optionnel mais bonne pratique)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(20), default='none') # ex: 'one_time', 'pro_annual'
    is_active = db.Column(db.Boolean, default=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # On ne stocke JAMAIS les mots de passe en clair
    password_hash = db.Column(db.String(256), nullable=False)
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)

    def set_password(self, password):
        """Crée un hash sécurisé du mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(50), nullable=False) # ex: 'pro_annual', 'team_basic'
    stripe_subscription_id = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active') # active, canceled, past_due
    current_period_end = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} for User {self.user_id}>'