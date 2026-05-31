# tests/test_crm.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import csv
import pytest
import datetime
from app import create_app, db
from app.models import User, Contact, ContactNote, Task, Subscription
from app.extensions import limiter
from werkzeug.security import generate_password_hash


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test'
    STRIPE_SECRET_KEY = 'sk_test'
    STRIPE_PUBLIC_KEY = 'pk_test'
    WTF_CSRF_ENABLED = False
    SENDGRID_API_KEY = None
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
def user(app_instance):
    u = User(
        username='jean',
        email='jean@mail.com',
        password_hash=generate_password_hash('JeanPass123'),
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def other_user(app_instance):
    u = User(
        username='marie',
        email='marie@mail.com',
        password_hash=generate_password_hash('MariePass123'),
    )
    db.session.add(u)
    db.session.commit()
    return u


def login(client, username, password):
    return client.post('/auth/login', json={'username': username, 'password': password})


def make_contact(client, extra=None):
    data = {'first_name': 'Pierre', 'last_name': 'Tremblay',
            'email': 'pierre@mail.com', 'phone': '5141234567'}
    if extra:
        data.update(extra)
    return client.post('/api/v1/crm/contacts', json=data)


# ── Dashboard ─────────────────────────────────────────────────────────────────

def test_dashboard_empty(client, user):
    login(client, 'jean', 'JeanPass123')
    rv = client.get('/api/v1/crm/dashboard')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total_contacts'] == 0
    assert data['conversion_rate'] == 0
    assert 'pipeline' in data


def test_dashboard_with_contacts(client, user):
    login(client, 'jean', 'JeanPass123')
    make_contact(client)
    make_contact(client, {'first_name': 'Marc', 'email': 'marc@mail.com'})
    rv = client.get('/api/v1/crm/dashboard')
    assert rv.get_json()['total_contacts'] == 2


# ── Contacts CRUD ─────────────────────────────────────────────────────────────

def test_create_and_list_contacts(client, user):
    login(client, 'jean', 'JeanPass123')
    rv = make_contact(client)
    assert rv.status_code == 201
    assert rv.get_json()['id']

    rv = client.get('/api/v1/crm/contacts')
    assert rv.status_code == 200
    assert rv.get_json()['total'] == 1


def test_contact_requires_first_name(client, user):
    login(client, 'jean', 'JeanPass123')
    rv = client.post('/api/v1/crm/contacts', json={'email': 'x@mail.com'})
    assert rv.status_code == 400


def test_get_contact_detail(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.get(f'/api/v1/crm/contacts/{cid}')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['first_name'] == 'Pierre'
    assert 'notes' in data
    assert 'tasks' in data


def test_update_contact(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.put(f'/api/v1/crm/contacts/{cid}', json={'city': 'Montréal'})
    assert rv.status_code == 200
    rv = client.get(f'/api/v1/crm/contacts/{cid}')
    assert rv.get_json()['city'] == 'Montréal'


def test_delete_contact(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.delete(f'/api/v1/crm/contacts/{cid}')
    assert rv.status_code == 200
    rv = client.get('/api/v1/crm/contacts')
    assert rv.get_json()['total'] == 0


def test_contact_forbidden_for_other_user(client, user, other_user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    client.post('/auth/logout')

    login(client, 'marie', 'MariePass123')
    assert client.get(f'/api/v1/crm/contacts/{cid}').status_code == 403
    assert client.put(f'/api/v1/crm/contacts/{cid}', json={}).status_code == 403
    assert client.delete(f'/api/v1/crm/contacts/{cid}').status_code == 403


# ── Pipeline ──────────────────────────────────────────────────────────────────

def test_pipeline_view(client, user):
    login(client, 'jean', 'JeanPass123')
    make_contact(client)
    rv = client.get('/api/v1/crm/pipeline')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'new' in data
    assert data['new']['count'] == 1


def test_update_stage(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.patch(f'/api/v1/crm/contacts/{cid}/stage', json={'stage': 'contacted'})
    assert rv.status_code == 200
    rv = client.get(f'/api/v1/crm/contacts/{cid}')
    assert rv.get_json()['pipeline_stage'] == 'contacted'


def test_invalid_stage_rejected(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.patch(f'/api/v1/crm/contacts/{cid}/stage', json={'stage': 'peut_etre'})
    assert rv.status_code == 400


# ── Notes ─────────────────────────────────────────────────────────────────────

def test_add_and_list_notes(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.post(f'/api/v1/crm/contacts/{cid}/notes',
                     json={'content': 'Client intéressé pour peinture salon.'})
    assert rv.status_code == 201
    note_id = rv.get_json()['id']

    rv = client.get(f'/api/v1/crm/contacts/{cid}/notes')
    assert len(rv.get_json()) == 1

    rv = client.delete(f'/api/v1/crm/notes/{note_id}')
    assert rv.status_code == 200


def test_empty_note_rejected(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    rv = client.post(f'/api/v1/crm/contacts/{cid}/notes', json={'content': ''})
    assert rv.status_code == 400


# ── Tâches ────────────────────────────────────────────────────────────────────

def test_create_and_list_tasks(client, user):
    login(client, 'jean', 'JeanPass123')
    rv = client.post('/api/v1/crm/tasks', json={
        'title': 'Rappeler Pierre demain',
        'priority': 'high',
        'due_date': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
    })
    assert rv.status_code == 201

    rv = client.get('/api/v1/crm/tasks')
    assert rv.get_json()['total'] == 1


def test_toggle_task_done(client, user):
    login(client, 'jean', 'JeanPass123')
    tid = client.post('/api/v1/crm/tasks',
                      json={'title': 'À faire'}).get_json()['id']
    rv = client.patch(f'/api/v1/crm/tasks/{tid}/done')
    assert rv.get_json()['is_done'] is True
    rv = client.patch(f'/api/v1/crm/tasks/{tid}/done')
    assert rv.get_json()['is_done'] is False


def test_filter_tasks_not_done(client, user):
    login(client, 'jean', 'JeanPass123')
    tid = client.post('/api/v1/crm/tasks',
                      json={'title': 'Tâche 1'}).get_json()['id']
    client.post('/api/v1/crm/tasks', json={'title': 'Tâche 2'})
    client.patch(f'/api/v1/crm/tasks/{tid}/done')

    rv = client.get('/api/v1/crm/tasks?done=false')
    assert rv.get_json()['total'] == 1


def test_invalid_due_date(client, user):
    login(client, 'jean', 'JeanPass123')
    rv = client.post('/api/v1/crm/tasks',
                     json={'title': 'T', 'due_date': 'pas-une-date'})
    assert rv.status_code == 400


# ── Import / Export CSV ───────────────────────────────────────────────────────

def test_import_csv(client, user):
    login(client, 'jean', 'JeanPass123')
    csv_content = (
        "Prénom,Nom,Courriel,Téléphone,Entreprise,Ville\n"
        "Pierre,Tremblay,pierre@mail.com,5141234567,Peinture Pro,Montréal\n"
        "Marie,Dupont,marie@mail.com,4381234567,,Laval\n"
    )
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'contacts.csv'),
    }
    rv = client.post('/api/v1/crm/contacts/import', data=data,
                     content_type='multipart/form-data')
    assert rv.status_code == 200
    result = rv.get_json()
    assert result['imported'] == 2
    assert result['skipped'] == 0

    rv = client.get('/api/v1/crm/contacts')
    assert rv.get_json()['total'] == 2


def test_import_csv_full_name_column(client, user):
    login(client, 'jean', 'JeanPass123')
    csv_content = "name,email\nJean Peintre,jean@mail.com\n"
    data = {'file': (io.BytesIO(csv_content.encode()), 'c.csv')}
    rv = client.post('/api/v1/crm/contacts/import', data=data,
                     content_type='multipart/form-data')
    assert rv.get_json()['imported'] == 1
    rv = client.get('/api/v1/crm/contacts')
    contact = rv.get_json()['items'][0]
    assert contact['first_name'] == 'Jean'
    assert contact['last_name'] == 'Peintre'


def test_import_skips_rows_without_name(client, user):
    login(client, 'jean', 'JeanPass123')
    csv_content = "first_name,email\n,orphan@mail.com\nPierre,ok@mail.com\n"
    data = {'file': (io.BytesIO(csv_content.encode()), 'c.csv')}
    rv = client.post('/api/v1/crm/contacts/import', data=data,
                     content_type='multipart/form-data')
    result = rv.get_json()
    assert result['imported'] == 1
    assert result['skipped'] == 1


def test_export_csv(client, user):
    login(client, 'jean', 'JeanPass123')
    make_contact(client)
    rv = client.get('/api/v1/crm/contacts/export')
    assert rv.status_code == 200
    assert 'text/csv' in rv.content_type
    reader = csv.DictReader(io.StringIO(rv.data.decode('utf-8')))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]['Prénom'] == 'Pierre'


# ── Recherche ─────────────────────────────────────────────────────────────────

def test_search_contacts(client, user):
    login(client, 'jean', 'JeanPass123')
    make_contact(client, {'first_name': 'Pierre', 'email': 'pierre@mail.com'})
    make_contact(client, {'first_name': 'Marie', 'email': 'marie@mail.com'})

    rv = client.get('/api/v1/crm/contacts?q=pierre')
    assert rv.get_json()['total'] == 1
    assert rv.get_json()['items'][0]['first_name'] == 'Pierre'


def test_filter_by_stage(client, user):
    login(client, 'jean', 'JeanPass123')
    cid = make_contact(client).get_json()['id']
    client.patch(f'/api/v1/crm/contacts/{cid}/stage', json={'stage': 'won'})
    make_contact(client, {'first_name': 'Autre', 'email': 'autre@mail.com'})

    rv = client.get('/api/v1/crm/contacts?stage=won')
    assert rv.get_json()['total'] == 1
    rv = client.get('/api/v1/crm/contacts?stage=new')
    assert rv.get_json()['total'] == 1
