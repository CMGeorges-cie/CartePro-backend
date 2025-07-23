# tests/test_admin.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User
from flask import url_for
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user():
    user = User(username="admin", email="admin@mail.com", password=generate_password_hash("adminpass"), role="admin")
    db.session.add(user)
    db.session.commit()
    return user

def login(client, username, password):
    return client.post('/auth/login', json={
        'username': username,
        'password': password
    })

def test_admin_routes(client, admin_user):
    login(client, "admin", "adminpass")

    # Liste des utilisateurs
    rv = client.get('/api/v1/admin/users')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

    # Liste des cartes
    rv = client.get('/api/v1/admin/cards')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

    # Liste des backups
    rv = client.get('/api/v1/admin/backups')
    assert rv.status_code == 200
    assert "backups" in rv.get_json()