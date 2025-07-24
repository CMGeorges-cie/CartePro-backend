# tests/test_admin.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User
from app.extensions import limiter
from werkzeug.security import generate_password_hash

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test'
    STRIPE_SECRET_KEY = 'sk_test'
    WTF_CSRF_ENABLED = False

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
def admin_user(app_instance):
    user = User(username="admin", email="admin@mail.com", password_hash=generate_password_hash("adminpass"), role="admin", is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username, password):
    return client.post('/auth/login', json={
        'username': username,
        'password': password
    })


def test_admin_routes(client, admin_user):
    # Connexion de l'utilisateur admin
    rv = login(client, "admin", "adminpass")
    assert rv.status_code == 200
    assert "Login" in rv.get_json()["message"]

    rv = client.get('/api/v1/admin/users?page=1&per_page=1')
    assert rv.status_code == 200
    data = rv.get_json()
    assert "items" in data
    assert isinstance(data["items"], list)

    rv = client.get('/api/v1/admin/cards?page=1&per_page=1')
    assert rv.status_code == 200
    data = rv.get_json()
    assert "items" in data
    assert isinstance(data["items"], list)

    rv = client.get('/api/v1/admin/backups?page=1&per_page=1')
    assert rv.status_code == 200
    data = rv.get_json()
    assert "items" in data
    assert isinstance(data["items"], list)

    rv = client.get('/api/v1/admin/users', query_string={'email': 'admin@mail.com'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['email'] == 'admin@mail.com'

    # Create and delete a card then restore it
    rv = client.post('/api/v1/cards/', json={
        'name': 'Admin Card',
        'email': 'admin@mail.com',
        'title': 'Boss'
    })
    card_id = rv.get_json()['id']
    client.delete(f'/api/v1/cards/{card_id}')
    rv = client.post(f'/api/v1/admin/restore_card/{card_id}')
    assert rv.status_code == 200

