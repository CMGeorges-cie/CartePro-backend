# tests/test_pro_features.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest
from app import create_app, db
from app.models import User, Card, ScanEvent, Photo, QuoteRequest, Subscription
from app.extensions import limiter
from werkzeug.security import generate_password_hash
import datetime


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test'
    STRIPE_SECRET_KEY = 'sk_test'
    STRIPE_PUBLIC_KEY = 'pk_test'
    WTF_CSRF_ENABLED = False
    SENDGRID_API_KEY = None     # emails loggés seulement en test
    FROM_EMAIL = 'test@cartepro.ca'
    APP_URL = 'http://localhost:3000'


@pytest.fixture
def app_instance():
    app = create_app(TestConfig)
    limiter.reset()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def pro_user(app_instance):
    user = User(
        username='pro',
        email='pro@mail.com',
        password_hash=generate_password_hash('ProPass123'),
        is_admin=False,
    )
    db.session.add(user)
    db.session.flush()
    sub = Subscription(
        user_id=user.id,
        plan_name='pro_monthly',
        stripe_subscription_id='sub_test_pro',
        status='active',
        current_period_end=datetime.datetime(2099, 1, 1),
    )
    db.session.add(sub)
    db.session.commit()
    return user


@pytest.fixture
def free_user(app_instance):
    user = User(
        username='free',
        email='free@mail.com',
        password_hash=generate_password_hash('FreePass123'),
    )
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username, password):
    return client.post('/auth/login', json={'username': username, 'password': password})


def create_card(client, extra=None):
    data = {'name': 'Jean Peintre', 'email': 'jean@mail.com', 'title': 'Maître peintre'}
    if extra:
        data.update(extra)
    return client.post('/api/v1/cards/', json=data)


# ── Champs Pro sur la carte ────────────────────────────────────────────────────

def test_card_pro_fields(client, pro_user):
    login(client, 'pro', 'ProPass123')
    rv = create_card(client, {
        'trade': 'peintre',
        'service_zone': 'Rive-Sud, Montréal',
        'bio': 'Maître peintre depuis 20 ans.',
        'google_review_url': 'https://g.page/r/xxx',
        'facebook_url': 'https://facebook.com/jeanpeintre',
        'whatsapp_number': '+15141234567',
    })
    assert rv.status_code == 201
    card_id = rv.get_json()['id']

    rv = client.get(f'/api/v1/cards/{card_id}')
    data = rv.get_json()
    assert data['trade'] == 'peintre'
    assert data['service_zone'] == 'Rive-Sud, Montréal'
    assert data['bio'] == 'Maître peintre depuis 20 ans.'
    assert data['google_review_url'] == 'https://g.page/r/xxx'
    assert data['whatsapp_number'] == '+15141234567'


def test_update_card_pro_fields(client, pro_user):
    login(client, 'pro', 'ProPass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']

    rv = client.put(f'/api/v1/cards/{card_id}', json={
        'trade': 'électricien',
        'service_zone': 'Laval',
    })
    assert rv.status_code == 200

    rv = client.get(f'/api/v1/cards/{card_id}')
    assert rv.get_json()['trade'] == 'électricien'
    assert rv.get_json()['service_zone'] == 'Laval'


# ── Tracking des scans ─────────────────────────────────────────────────────────

def test_record_scan_public(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    rv = client.post(f'/api/v1/cards/{card_id}/scan')
    assert rv.status_code == 201
    assert 'Scan enregistré' in rv.get_json()['message']


def test_scan_stats_owner_only(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post(f'/api/v1/cards/{card_id}/scan')

    rv = client.get(f'/api/v1/cards/{card_id}/scans')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    assert data['items'][0]['card_id'] == card_id


def test_scan_stats_forbidden_for_other_user(client, free_user, app_instance):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    other = User(
        username='other', email='other@mail.com',
        password_hash=generate_password_hash('OtherPass123'),
    )
    with app_instance.app_context():
        db.session.add(other)
        db.session.commit()

    login(client, 'other', 'OtherPass123')
    rv = client.get(f'/api/v1/cards/{card_id}/scans')
    assert rv.status_code == 403


def test_scan_deleted_card_returns_404(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.delete(f'/api/v1/cards/{card_id}')
    client.post('/auth/logout')

    rv = client.post(f'/api/v1/cards/{card_id}/scan')
    assert rv.status_code == 404


# ── Galerie photos ─────────────────────────────────────────────────────────────

def test_upload_and_list_photos(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']

    data = {
        'photo': (io.BytesIO(b'fake-image-data'), 'chantier.jpg'),
        'photo_type': 'after',
        'caption': 'Résultat final',
    }
    rv = client.post(
        f'/api/v1/cards/{card_id}/photos',
        data=data,
        content_type='multipart/form-data',
    )
    assert rv.status_code == 201
    photo_id = rv.get_json()['id']

    rv = client.get(f'/api/v1/cards/{card_id}/photos')
    assert rv.status_code == 200
    photos = rv.get_json()
    assert len(photos) == 1
    assert photos[0]['photo_type'] == 'after'
    assert photos[0]['caption'] == 'Résultat final'

    rv = client.delete(f'/api/v1/cards/{card_id}/photos/{photo_id}')
    assert rv.status_code == 200

    rv = client.get(f'/api/v1/cards/{card_id}/photos')
    assert len(rv.get_json()) == 0


def test_upload_photo_invalid_extension(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']

    data = {'photo': (io.BytesIO(b'not-an-image'), 'script.py')}
    rv = client.post(
        f'/api/v1/cards/{card_id}/photos',
        data=data,
        content_type='multipart/form-data',
    )
    assert rv.status_code == 400


def test_upload_photo_forbidden(client, free_user, app_instance):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    other = User(
        username='other2', email='other2@mail.com',
        password_hash=generate_password_hash('OtherPass123'),
    )
    with app_instance.app_context():
        db.session.add(other)
        db.session.commit()

    login(client, 'other2', 'OtherPass123')
    data = {'photo': (io.BytesIO(b'img'), 'photo.jpg')}
    rv = client.post(
        f'/api/v1/cards/{card_id}/photos',
        data=data,
        content_type='multipart/form-data',
    )
    assert rv.status_code == 403


# ── Demandes de soumission ─────────────────────────────────────────────────────

def test_quote_request_public(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    rv = client.post(f'/api/v1/cards/{card_id}/quote', json={
        'name': 'Marie Tremblay',
        'email': 'marie@mail.com',
        'phone': '5141234567',
        'message': 'J\'aimerais une soumission pour peindre mon salon.',
    })
    assert rv.status_code == 201
    assert 'envoyée' in rv.get_json()['message']


def test_quote_request_requires_name_and_email(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    rv = client.post(f'/api/v1/cards/{card_id}/quote', json={'name': 'Marie'})
    assert rv.status_code == 400


def test_list_quotes_owner_only(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.post('/auth/logout')

    client.post(f'/api/v1/cards/{card_id}/quote', json={
        'name': 'Client Test', 'email': 'client@mail.com',
    })

    login(client, 'free', 'FreePass123')
    rv = client.get(f'/api/v1/cards/{card_id}/quotes')
    assert rv.status_code == 200
    assert rv.get_json()['total'] == 1


def test_quote_on_deleted_card(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = create_card(client)
    card_id = rv.get_json()['id']
    client.delete(f'/api/v1/cards/{card_id}')
    client.post('/auth/logout')

    rv = client.post(f'/api/v1/cards/{card_id}/quote', json={
        'name': 'Client', 'email': 'c@mail.com',
    })
    assert rv.status_code == 404


# ── Stripe Checkout ────────────────────────────────────────────────────────────

def test_stripe_config_requires_auth(client):
    rv = client.get('/api/v1/stripe/config')
    assert rv.status_code in (401, 302)


def test_stripe_checkout_invalid_plan(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = client.post('/api/v1/stripe/create-checkout', json={'plan': 'premium_gold'})
    assert rv.status_code == 400


def test_stripe_checkout_no_price_configured(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = client.post('/api/v1/stripe/create-checkout', json={'plan': 'monthly'})
    assert rv.status_code == 503


def test_stripe_portal_no_subscription(client, free_user):
    login(client, 'free', 'FreePass123')
    rv = client.get('/api/v1/stripe/portal')
    assert rv.status_code == 404
