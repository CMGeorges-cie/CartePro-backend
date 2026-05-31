"""
CRM — Gestion des contacts, pipeline, notes et tâches.
Tous les endpoints requièrent une authentification.
"""
import csv
import io
import datetime

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app.models import (
    Contact, ContactNote, Task, QuoteRequest,
    PIPELINE_STAGES, db,
)
from app.errors import APIError, commit_session, get_or_404
from app.utils import paginate_query

crm_bp = Blueprint('crm', __name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@crm_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Statistiques CRM globales pour l'utilisateur connecté."""
    uid = current_user.id
    total = Contact.query.filter_by(user_id=uid).count()
    won = Contact.query.filter_by(user_id=uid, pipeline_stage='won').count()
    conversion = round(won / total * 100, 1) if total else 0

    today = datetime.datetime.utcnow().date()
    tomorrow = today + datetime.timedelta(days=1)
    tasks_due = Task.query.filter(
        Task.user_id == uid,
        Task.is_done == False,
        Task.due_date >= datetime.datetime.combine(today, datetime.time.min),
        Task.due_date < datetime.datetime.combine(tomorrow, datetime.time.min),
    ).count()

    stage_counts = {stage: 0 for stage in PIPELINE_STAGES}
    rows = (
        db.session.query(Contact.pipeline_stage, db.func.count())
        .filter_by(user_id=uid)
        .group_by(Contact.pipeline_stage)
        .all()
    )
    for stage, count in rows:
        if stage in stage_counts:
            stage_counts[stage] = count

    recent = (
        Contact.query.filter_by(user_id=uid)
        .order_by(Contact.created_at.desc())
        .limit(5)
        .all()
    )

    return jsonify({
        'total_contacts': total,
        'conversion_rate': conversion,
        'tasks_due_today': tasks_due,
        'pipeline': stage_counts,
        'recent_contacts': [c.serialize() for c in recent],
    })


# ── Pipeline (vue kanban) ──────────────────────────────────────────────────────

@crm_bp.route('/pipeline', methods=['GET'])
@login_required
def pipeline():
    """Retourne les contacts groupés par étape du pipeline."""
    uid = current_user.id
    result = {}
    for stage in PIPELINE_STAGES:
        contacts = (
            Contact.query.filter_by(user_id=uid, pipeline_stage=stage)
            .order_by(Contact.updated_at.desc())
            .all()
        )
        result[stage] = {
            'count': len(contacts),
            'contacts': [c.serialize() for c in contacts],
        }
    return jsonify(result)


# ── Contacts ──────────────────────────────────────────────────────────────────

@crm_bp.route('/contacts', methods=['GET'])
@login_required
def list_contacts():
    """Liste les contacts avec filtres optionnels (stage, search, source)."""
    uid = current_user.id
    query = Contact.query.filter_by(user_id=uid)

    stage = request.args.get('stage')
    if stage and stage in PIPELINE_STAGES:
        query = query.filter_by(pipeline_stage=stage)

    source = request.args.get('source')
    if source:
        query = query.filter_by(source=source)

    search = request.args.get('q', '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Contact.first_name.ilike(like),
                Contact.last_name.ilike(like),
                Contact.email.ilike(like),
                Contact.phone.ilike(like),
                Contact.company.ilike(like),
            )
        )

    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    sort_col = getattr(Contact, sort, Contact.created_at)
    query = query.order_by(sort_col.desc() if order == 'desc' else sort_col.asc())

    return jsonify(paginate_query(query))


@crm_bp.route('/contacts', methods=['POST'])
@login_required
def create_contact():
    """Crée un contact manuellement."""
    data = request.get_json(silent=True) or {}
    first_name = (data.get('first_name') or '').strip()
    if not first_name:
        raise APIError("Le prénom est requis.", 400)

    contact = Contact(
        user_id=current_user.id,
        first_name=first_name,
        last_name=(data.get('last_name') or '').strip() or None,
        email=(data.get('email') or '').strip() or None,
        phone=(data.get('phone') or '').strip() or None,
        company=(data.get('company') or '').strip() or None,
        address=(data.get('address') or '').strip() or None,
        city=(data.get('city') or '').strip() or None,
        pipeline_stage=data.get('pipeline_stage', 'new'),
        source='manual',
    )
    db.session.add(contact)
    commit_session("Impossible de créer le contact.")
    return jsonify({'message': 'Contact créé.', 'id': contact.id}), 201


@crm_bp.route('/contacts/<int:contact_id>', methods=['GET'])
@login_required
def get_contact(contact_id):
    """Détail d'un contact avec ses notes et tâches."""
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = contact.serialize()
    data['notes'] = [n.serialize() for n in contact.notes]
    data['tasks'] = [t.serialize() for t in contact.tasks]
    return jsonify(data)


@crm_bp.route('/contacts/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = request.get_json(silent=True) or {}
    for field in ('first_name', 'last_name', 'email', 'phone', 'company',
                  'address', 'city'):
        if field in data:
            setattr(contact, field, (data[field] or '').strip() or None)
    if 'pipeline_stage' in data and data['pipeline_stage'] in PIPELINE_STAGES:
        contact.pipeline_stage = data['pipeline_stage']
    contact.updated_at = datetime.datetime.utcnow()
    commit_session("Impossible de mettre à jour le contact.")
    return jsonify({'message': 'Contact mis à jour.'})


@crm_bp.route('/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    db.session.delete(contact)
    commit_session("Impossible de supprimer le contact.")
    return jsonify({'message': 'Contact supprimé.'})


@crm_bp.route('/contacts/<int:contact_id>/stage', methods=['PATCH'])
@login_required
def update_stage(contact_id):
    """Déplace un contact vers une autre étape du pipeline."""
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = request.get_json(silent=True) or {}
    stage = data.get('stage')
    if stage not in PIPELINE_STAGES:
        raise APIError(
            f"Étape invalide. Valeurs acceptées : {', '.join(PIPELINE_STAGES)}", 400
        )
    contact.pipeline_stage = stage
    contact.updated_at = datetime.datetime.utcnow()
    commit_session("Impossible de mettre à jour l'étape.")
    return jsonify({'message': 'Étape mise à jour.', 'stage': stage})


# ── Promotion de soumission → contact ─────────────────────────────────────────

@crm_bp.route('/contacts/from-quote/<int:quote_id>', methods=['POST'])
@login_required
def contact_from_quote(quote_id):
    """Crée un contact CRM à partir d'une demande de soumission existante."""
    quote = get_or_404(QuoteRequest, quote_id)
    # Vérifie que la carte appartient à l'utilisateur
    from app.models import Card
    card = db.session.get(Card, quote.card_id)
    if not card or card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    if Contact.query.filter_by(user_id=current_user.id,
                               quote_request_id=quote_id).first():
        raise APIError("Un contact existe déjà pour cette soumission.", 409)

    parts = quote.requester_name.strip().split(' ', 1)
    contact = Contact(
        user_id=current_user.id,
        first_name=parts[0],
        last_name=parts[1] if len(parts) > 1 else None,
        email=quote.requester_email,
        phone=quote.requester_phone,
        source='quote_request',
        quote_request_id=quote_id,
        pipeline_stage='new',
    )
    if quote.message:
        db.session.add(contact)
        db.session.flush()
        note = ContactNote(
            contact_id=contact.id,
            user_id=current_user.id,
            content=f"Message initial : {quote.message}",
        )
        db.session.add(note)
    else:
        db.session.add(contact)
    commit_session("Impossible de créer le contact.")
    return jsonify({'message': 'Contact créé depuis la soumission.', 'id': contact.id}), 201


# ── Notes ─────────────────────────────────────────────────────────────────────

@crm_bp.route('/contacts/<int:contact_id>/notes', methods=['GET'])
@login_required
def list_notes(contact_id):
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    notes = ContactNote.query.filter_by(contact_id=contact_id)\
        .order_by(ContactNote.created_at.desc()).all()
    return jsonify([n.serialize() for n in notes])


@crm_bp.route('/contacts/<int:contact_id>/notes', methods=['POST'])
@login_required
def add_note(contact_id):
    contact = get_or_404(Contact, contact_id)
    if contact.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        raise APIError("Le contenu de la note est requis.", 400)
    note = ContactNote(
        contact_id=contact_id,
        user_id=current_user.id,
        content=content,
    )
    db.session.add(note)
    commit_session("Impossible d'ajouter la note.")
    return jsonify({'message': 'Note ajoutée.', 'id': note.id}), 201


@crm_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = get_or_404(ContactNote, note_id)
    if note.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    db.session.delete(note)
    commit_session("Impossible de supprimer la note.")
    return jsonify({'message': 'Note supprimée.'})


# ── Tâches ────────────────────────────────────────────────────────────────────

@crm_bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    """Liste les tâches avec filtres (done, due_today, contact_id, priority)."""
    query = Task.query.filter_by(user_id=current_user.id)

    if request.args.get('done') == 'false':
        query = query.filter_by(is_done=False)
    elif request.args.get('done') == 'true':
        query = query.filter_by(is_done=True)

    if request.args.get('due_today') == 'true':
        today = datetime.datetime.utcnow().date()
        query = query.filter(
            Task.due_date >= datetime.datetime.combine(today, datetime.time.min),
            Task.due_date < datetime.datetime.combine(
                today + datetime.timedelta(days=1), datetime.time.min
            ),
        )

    if request.args.get('overdue') == 'true':
        query = query.filter(
            Task.is_done == False,
            Task.due_date < datetime.datetime.utcnow(),
        )

    contact_id = request.args.get('contact_id', type=int)
    if contact_id:
        query = query.filter_by(contact_id=contact_id)

    priority = request.args.get('priority')
    if priority in ('low', 'medium', 'high'):
        query = query.filter_by(priority=priority)

    query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    return jsonify(paginate_query(query))


@crm_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    if not title:
        raise APIError("Le titre de la tâche est requis.", 400)

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.datetime.fromisoformat(data['due_date'])
        except ValueError:
            raise APIError("Format de date invalide. Utilisez ISO 8601.", 400)

    task = Task(
        user_id=current_user.id,
        contact_id=data.get('contact_id'),
        title=title,
        description=(data.get('description') or '').strip() or None,
        due_date=due_date,
        priority=data.get('priority', 'medium'),
    )
    db.session.add(task)
    commit_session("Impossible de créer la tâche.")
    return jsonify({'message': 'Tâche créée.', 'id': task.id}), 201


@crm_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = get_or_404(Task, task_id)
    if task.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        task.title = (data['title'] or '').strip()
    if 'description' in data:
        task.description = (data['description'] or '').strip() or None
    if 'priority' in data and data['priority'] in ('low', 'medium', 'high'):
        task.priority = data['priority']
    if 'contact_id' in data:
        task.contact_id = data['contact_id']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.datetime.fromisoformat(data['due_date'])
            except ValueError:
                raise APIError("Format de date invalide.", 400)
        else:
            task.due_date = None
    commit_session("Impossible de mettre à jour la tâche.")
    return jsonify({'message': 'Tâche mise à jour.'})


@crm_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = get_or_404(Task, task_id)
    if task.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    db.session.delete(task)
    commit_session("Impossible de supprimer la tâche.")
    return jsonify({'message': 'Tâche supprimée.'})


@crm_bp.route('/tasks/<int:task_id>/done', methods=['PATCH'])
@login_required
def toggle_task(task_id):
    """Bascule l'état fait/non-fait d'une tâche."""
    task = get_or_404(Task, task_id)
    if task.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    task.is_done = not task.is_done
    commit_session("Impossible de mettre à jour la tâche.")
    return jsonify({'message': 'Tâche mise à jour.', 'is_done': task.is_done})


# ── Import / Export CSV ───────────────────────────────────────────────────────

_CSV_FIELD_ALIASES = {
    'prenom': 'first_name', 'prénom': 'first_name', 'firstname': 'first_name',
    'nom': 'last_name', 'lastname': 'last_name', 'surname': 'last_name',
    'courriel': 'email', 'mail': 'email',
    'telephone': 'phone', 'téléphone': 'phone', 'tel': 'phone',
    'entreprise': 'company', 'organisation': 'company', 'organization': 'company',
    'adresse': 'address',
    'ville': 'city',
    'nom complet': 'full_name', 'full name': 'full_name', 'name': 'full_name',
}


def _normalize_header(h: str) -> str:
    return _CSV_FIELD_ALIASES.get(h.strip().lower(), h.strip().lower())


@crm_bp.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    """Importe des contacts depuis un fichier CSV.

    Colonnes reconnues (FR et EN) : prénom/firstname, nom/lastname, name/full_name,
    email/courriel, téléphone/phone, entreprise/company, adresse/address, ville/city.
    """
    if 'file' not in request.files:
        raise APIError("Aucun fichier CSV fourni.", 400)
    file = request.files['file']
    if not file.filename.lower().endswith('.csv'):
        raise APIError("Le fichier doit être au format CSV.", 400)

    try:
        content = file.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        content = file.read().decode('latin-1')

    reader = csv.DictReader(io.StringIO(content))
    headers = {_normalize_header(h): h for h in (reader.fieldnames or [])}

    imported, skipped, errors = 0, 0, []

    for i, row in enumerate(reader, start=2):
        norm = {_normalize_header(k): v for k, v in row.items()}

        # Gestion colonne "full_name" (ex: export Google Contacts)
        first_name = (norm.get('first_name') or '').strip()
        last_name = (norm.get('last_name') or '').strip() or None

        if not first_name and norm.get('full_name'):
            parts = norm['full_name'].strip().split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else None

        if not first_name:
            errors.append(f"Ligne {i} ignorée : prénom manquant.")
            skipped += 1
            continue

        contact = Contact(
            user_id=current_user.id,
            first_name=first_name,
            last_name=last_name,
            email=(norm.get('email') or '').strip() or None,
            phone=(norm.get('phone') or '').strip() or None,
            company=(norm.get('company') or '').strip() or None,
            address=(norm.get('address') or '').strip() or None,
            city=(norm.get('city') or '').strip() or None,
            source='import',
        )
        db.session.add(contact)
        imported += 1

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise APIError("Erreur lors de l'enregistrement des contacts.", 500) from exc

    return jsonify({
        'message': f'{imported} contact(s) importé(s).',
        'imported': imported,
        'skipped': skipped,
        'errors': errors[:20],  # max 20 erreurs retournées
    })


@crm_bp.route('/contacts/export', methods=['GET'])
@login_required
def export_contacts():
    """Exporte tous les contacts au format CSV."""
    stage = request.args.get('stage')
    query = Contact.query.filter_by(user_id=current_user.id)
    if stage and stage in PIPELINE_STAGES:
        query = query.filter_by(pipeline_stage=stage)

    contacts = query.order_by(Contact.created_at.desc()).all()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'ID', 'Prénom', 'Nom', 'Courriel', 'Téléphone', 'Entreprise',
        'Adresse', 'Ville', 'Étape pipeline', 'Source', 'Créé le',
    ])
    for c in contacts:
        writer.writerow([
            c.id, c.first_name, c.last_name or '', c.email or '',
            c.phone or '', c.company or '', c.address or '', c.city or '',
            c.pipeline_stage, c.source or '', c.created_at.strftime('%Y-%m-%d'),
        ])

    return si.getvalue(), 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="cartepro-contacts.csv"',
    }
