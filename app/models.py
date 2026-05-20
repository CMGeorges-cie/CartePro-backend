# app/models.py

from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime
from flask_login import UserMixin


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
    # Champs CartePro Pro — entrepreneurs en services manuels
    trade = db.Column(db.String(50), nullable=True)            # peintre, électricien, etc.
    service_zone = db.Column(db.String(200), nullable=True)    # ex: "Rive-Sud, Montréal"
    bio = db.Column(db.Text, nullable=True)
    google_review_url = db.Column(db.String(300), nullable=True)
    facebook_url = db.Column(db.String(300), nullable=True)
    whatsapp_number = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(20), default='none')
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    photos = db.relationship('Photo', backref='card', lazy=True, cascade='all, delete-orphan')
    scans = db.relationship('ScanEvent', backref='card', lazy=True, cascade='all, delete-orphan')
    quote_requests = db.relationship('QuoteRequest', backref='card', lazy=True, cascade='all, delete-orphan')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'instagram': self.instagram,
            'linkedin': self.linkedin,
            'trade': self.trade,
            'service_zone': self.service_zone,
            'bio': self.bio,
            'google_review_url': self.google_review_url,
            'facebook_url': self.facebook_url,
            'whatsapp_number': self.whatsapp_number,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'is_active': self.is_active,
            'is_deleted': self.is_deleted,
        }


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    avatar_filename = db.Column(db.String(200), nullable=True)
    cards = db.relationship('Card', backref='user', lazy=True)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)

    @property
    def is_pro(self) -> bool:
        return any(sub.status == 'active' for sub in self.subscriptions)

    @property
    def subscription_status(self) -> str:
        active = next((s for s in self.subscriptions if s.status == 'active'), None)
        return active.status if active else 'none'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_admin': self.is_admin,
            'stripe_customer_id': self.stripe_customer_id,
            'avatar_filename': self.avatar_filename,
            'is_pro': self.is_pro,
            'subscription_status': self.subscription_status,
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(50), nullable=False)
    stripe_subscription_id = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due
    current_period_end = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} for User {self.user_id}>'


class ScanEvent(db.Model):
    __tablename__ = 'scan_events'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(36), db.ForeignKey('cards.id'), nullable=False)
    scanned_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)   # IPv6 = max 45 chars
    user_agent = db.Column(db.String(300), nullable=True)
    city = db.Column(db.String(100), nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'scanned_at': self.scanned_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'city': self.city,
        }


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(36), db.ForeignKey('cards.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    photo_type = db.Column(db.String(10), default='after')  # 'before' ou 'after'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'filename': self.filename,
            'caption': self.caption,
            'photo_type': self.photo_type,
            'created_at': self.created_at.isoformat(),
        }


class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(36), db.ForeignKey('cards.id'), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_phone = db.Column(db.String(20), nullable=True)
    requester_email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'requester_name': self.requester_name,
            'requester_phone': self.requester_phone,
            'requester_email': self.requester_email,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
        }
