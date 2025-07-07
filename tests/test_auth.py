import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User, Card
from flask import url_for
from werkzeug.security import generate_password_hash
import requests

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
def session():
    return requests.Session()

def register(client, username, email, password):
    return client.post('/auth/register', json={
        'username': username,
        'email': email,
        'password': password
    })

def login(client, username, password):
    return client.post('/auth/login', json={
        'username': username,
        'password': password
    })

def logout(client):
    return client.post('/auth/logout')

def test_user_registration_and_login(client):
    # Register
    rv = register(client, "bob", "bob@mail.com", "1234")
    assert rv.status_code in (200, 201)  # 200 OK or 201 Created
    assert "User" in rv.get_json()["message"]

    # Login
    rv = login(client, "bob@mail.com", "1234")
    assert rv.status_code == 200
    assert b"Logged in successfully" in rv.data

    # Logout
    rv = logout(client)
    assert rv.status_code == 200
    assert b"Logged out successfully" in rv.data

def test_card_crud(client):
    # Register and login
    register(client, "alice", "alice@mail.com", "pass")
    login(client, "alice@mail.com", "pass")

    # Create card
    rv = client.post('/api/v1/cards', json={
        "name": "Alice Card",
        "email": "alice@mail.com",
        "title": "CEO"
    })
    assert rv.status_code == 201
    card_id = rv.get_json()["id"]

    # Get card
    rv = client.get(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 200
    assert rv.get_json()["name"] == "Alice Card"

    # Update card
    rv = client.put(f'/api/v1/cards/{card_id}', json={"title": "CTO"})
    assert rv.status_code == 200
    assert b"Card updated successfully" in rv.data

    # Delete card
    rv = client.delete(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 200
    assert b"Card deleted successfully" in rv.data

def test_protected_routes_require_login(client):
    # Try to create card without login
    rv = client.post('/api/v1/cards', json={
        "name": "NoAuth",
        "email": "noauth@mail.com",
        "title": "Hacker"
    })
    assert rv.status_code in (401, 302)  # 401 Unauthorized or 302 Redirect to login

def test_me_route(client):
    register(client, "bob", "bob@mail.com", "1234")
    login(client, "bob", "1234")
    rv = client.get('/auth/me')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["username"] == "bob"
