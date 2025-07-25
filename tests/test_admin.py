# tests/test_admin.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test'
    STRIPE_SECRET_KEY = 'sk_test'

@pytest.fixture
def app_instance():
    app = create_app(TestConfig)
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

    # Search user by email
    new_user = User(username="bob", email="bob@mail.com", password_hash=generate_password_hash("pwd"))
    db.session.add(new_user)
    db.session.commit()
    rv = client.get('/api/v1/admin/users?email=bob@mail.com')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["total"] >= 1
    assert any(u["email"] == "bob@mail.com" for u in data["items"]) if data["items"] else False

    # Restore deleted user
    new_user.username = f"deleted-{new_user.id}"
    new_user.email = f"deleted-{new_user.id}@example.com"
    new_user.is_deleted = True
    db.session.commit()
    rv = client.post(f'/api/v1/admin/users/{new_user.id}/restore', json={"username": "bob2", "email": "bob2@mail.com"})
    assert rv.status_code == 200
    assert "restored" in rv.get_json()["message"]

