# tests/test_auth.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User, Card
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
    assert rv.status_code in (200, 201)
    assert "User" in rv.get_json()["message"]

    # Login
    rv = login(client, "bob", "1234")
    assert rv.status_code == 200
    assert "Login" in rv.get_json()["message"]

    # Logout
    rv = logout(client)
    assert rv.status_code == 200
    assert "Logged out" in rv.get_json()["message"]


def test_card_crud(client):
    register(client, "alice", "alice@mail.com", "pass")
    login(client, "alice", "pass")

    rv = client.post('/api/v1/cards/', json={
        "name": "Alice Card",
        "email": "alice@mail.com",
        "title": "CEO"
    })
    assert rv.status_code == 201
    card_id = rv.get_json()["id"]

    rv = client.get(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 200
    assert rv.get_json()["name"] == "Alice Card"

    rv = client.put(f'/api/v1/cards/{card_id}', json={"title": "CTO"})
    assert rv.status_code == 200
    assert "updated" in rv.get_json()["message"]

    rv = client.delete(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 200
    assert "deleted" in rv.get_json()["message"]


def test_list_cards_with_pagination(client):
    register(client, "paginated", "paginated@mail.com", "pass")
    login(client, "paginated", "pass")

    for i in range(3):
        client.post('/api/v1/cards/', json={
            "name": f"Card {i}",
            "email": f"card{i}@mail.com",
            "title": "Title"
        })

    rv = client.get('/api/v1/cards/?page=1&per_page=2')
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 2


def test_protected_routes_require_login(client):
    rv = client.post('/api/v1/cards/', json={
        "name": "NoAuth",
        "email": "noauth@mail.com",
        "title": "Hacker"
    })
    assert rv.status_code in (401, 302)


def test_card_limit_free_plan(client):
    register(client, "limit", "limit@mail.com", "pass")
    login(client, "limit", "pass")
    rv = client.post('/api/v1/cards/', json={"name": "c1", "email": "e@mail.com", "title": "t"})
    assert rv.status_code == 201
    rv = client.post('/api/v1/cards/', json={"name": "c2", "email": "e2@mail.com", "title": "t"})
    assert rv.status_code == 403


def test_me_route(client):
    register(client, "bob", "bob@mail.com", "1234")
    login(client, "bob", "1234")
    rv = client.get('/auth/me')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["username"] == "bob"


def test_card_access_forbidden(client):
    register(client, "user1", "u1@mail.com", "pass")
    login(client, "user1", "pass")
    rv = client.post('/api/v1/cards/', json={
        "name": "User 1 Card",
        "email": "u1@mail.com",
        "title": "CTO"
    })
    card_id = rv.get_json()["id"]
    logout(client)

    register(client, "user2", "u2@mail.com", "pass")
    login(client, "user2", "pass")

    rv = client.get(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 403

    rv = client.put(f'/api/v1/cards/{card_id}', json={"title": "Stolen"})
    assert rv.status_code == 403

    rv = client.delete(f'/api/v1/cards/{card_id}')
    assert rv.status_code == 403


def test_update_me_and_delete(client):
    register(client, "jean", "jean@mail.com", "pw")
    login(client, "jean", "pw")
    rv = client.patch('/auth/me', json={'username': 'newjean'})
    assert rv.status_code == 200
    assert rv.get_json()['username'] == 'newjean'
    rv = client.delete('/auth/me')
    assert rv.status_code == 200
    # user should be anonymized
    rv = client.get('/auth/me')
    assert rv.status_code in (401, 302)


def test_stripe_webhook(client):
    event = {
        'type': 'customer.subscription.updated',
        'data': {'object': {'id': 'sub_123', 'status': 'active'}}
    }
    rv = client.post('/api/v1/stripe/webhook', json=event)
    assert rv.status_code == 200

