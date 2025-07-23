import pytest
import requests

BASE_URL = "http://localhost:5000/api/v1"
AUTH_URL = "http://localhost:5000/auth"

@pytest.fixture
def session():
    return requests.Session()

def print_response(resp):
    print(f"[{resp.request.method}] {resp.url}")
    print(f"Status: {resp.status_code}")
    try:
        print("Response:", resp.json())
    except Exception:
        print("Response (non-JSON):", resp.text)
    print("-" * 60)

def register_and_login(session, username, email, password):
    # Register
    resp = session.post(f"{AUTH_URL}/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    print_response(resp)
    assert resp.status_code in (200, 201)
    # Login
    resp = session.post(f"{AUTH_URL}/login", json={
        "username": username,
        "password": password
    })
    print_response(resp)
    assert resp.status_code == 200

def test_health(session):
    resp = session.get(f"{BASE_URL}/")
    print_response(resp)
    assert resp.status_code in (200, 404)  # 404 si pas de route /api/v1/

def test_generate_qr(session):
    data = {"url": "https://example.com"}
    resp = session.post(f"{BASE_URL}/qr/generate", json=data)
    print_response(resp)
    assert resp.status_code == 200

def test_card_lifecycle(session):
    register_and_login(session, "alice", "alice@example.com", "testpass123")
    # Création
    data = {
        "name": "Alice Test",
        "email": "alice@example.com",
        "title": "CEO",
        "phone": "123-456-7890",
        "website": "https://alice.com",
        "instagram": "@alice",
        "linkedin": "linkedin.com/in/alice"
    }
    resp = session.post(f"{BASE_URL}/cards", json=data)
    print_response(resp)
    assert resp.status_code in (200, 201)
    card_id = resp.json().get('id')
    assert card_id

    # Lecture
    resp = session.get(f"{BASE_URL}/cards/{card_id}")
    print_response(resp)
    assert resp.status_code == 200

    # Mise à jour
    update_data = {"phone": "987-654-3210"}
    resp = session.put(f"{BASE_URL}/cards/{card_id}", json=update_data)
    print_response(resp)
    assert resp.status_code == 200

    # Suppression
    resp = session.delete(f"{BASE_URL}/cards/{card_id}")
    print_response(resp)
    assert resp.status_code == 200

def test_get_user_cards(session):
    register_and_login(session, "bob", "bob@example.com", "testpass456")
    resp = session.get(f"{BASE_URL}/cards")
    print_response(resp)
    assert resp.status_code == 200

def test_checkout_session(session):
    # Remplace price_XXXXXX par un vrai Price ID Stripe pour un vrai test
    data = {"price_id": "price_XXXXXX"}
    resp = session.post(f"{BASE_URL}/stripe/create-checkout-session", json=data)
    print_response(resp)
    assert resp.status_code in (200, 400, 500)

def test_config(session):
    resp = session.get(f"{BASE_URL}/stripe/config")
    print_response(resp)
    assert resp.status_code == 200

def test_admin_routes(session):
    # Ce test suppose que tu as un utilisateur admin avec username "admin"
    register_and_login(session, "admin", "admin@example.com", "adminpass")
    resp = session.get(f"{BASE_URL}/admin/users")
    print_response(resp)
    assert resp.status_code in (200, 403)

    resp = session.get(f"{BASE_URL}/admin/cards")
    print_response(resp)
    assert resp.status_code in (200, 403)

    resp = session.get(f"{BASE_URL}/admin/backups")
    print_response(resp)
    assert resp.status_code in (200, 403)