from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid

from app.models import Card, Photo, ScanEvent, QuoteRequest, User, db
from app.errors import APIError, commit_session, get_or_404
from app.utils import paginate_query
from app.services import send_quote_notification_email

cards_bp = Blueprint('cards', __name__)

ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


# ── Cartes ────────────────────────────────────────────────────────────────────

@cards_bp.route('/', methods=['GET'])
@login_required
def list_cards():
    query = Card.query.filter_by(user_id=current_user.id)
    return jsonify(paginate_query(query))


@cards_bp.route('/', methods=['POST'])
@login_required
def create_card():
    """
    Créer une carte professionnelle.
    ---
    tags:
      - Cards
    parameters:
      - in: body
        name: card
        schema:
          type: object
          required: [name, email, title]
          properties:
            name:
              type: string
            email:
              type: string
            title:
              type: string
            phone:
              type: string
            website:
              type: string
            instagram:
              type: string
            linkedin:
              type: string
            trade:
              type: string
            service_zone:
              type: string
            bio:
              type: string
            google_review_url:
              type: string
            facebook_url:
              type: string
            whatsapp_number:
              type: string
    responses:
      201:
        description: Carte créée
      403:
        description: Limite de cartes atteinte (plan gratuit)
    """
    data = request.get_json(silent=True) or {}
    if not current_user.is_pro and Card.query.filter_by(user_id=current_user.id).count() >= 1:
        raise APIError("Limite de cartes atteinte. Passez au plan Pro pour en créer plusieurs.", 403)
    if not data.get('name') or not data.get('email') or not data.get('title'):
        raise APIError("Nom, courriel et titre sont requis.", 400)
    card = Card(
        user_id=current_user.id,
        name=data.get('name'),
        email=data.get('email'),
        title=data.get('title'),
        phone=data.get('phone'),
        website=data.get('website'),
        instagram=data.get('instagram'),
        linkedin=data.get('linkedin'),
        trade=data.get('trade'),
        service_zone=data.get('service_zone'),
        bio=data.get('bio'),
        google_review_url=data.get('google_review_url'),
        facebook_url=data.get('facebook_url'),
        whatsapp_number=data.get('whatsapp_number'),
    )
    db.session.add(card)
    commit_session("Impossible de créer la carte.")
    return jsonify({'message': 'Carte créée.', 'id': card.id}), 201


@cards_bp.route('/<string:card_id>', methods=['GET'])
@login_required
def get_card(card_id):
    card = get_or_404(Card, card_id)
    if card.is_deleted:
        raise APIError("Cette carte a été supprimée.", 404)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    return jsonify(card.serialize())


@cards_bp.route('/<string:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    card = get_or_404(Card, card_id)
    if card.is_deleted:
        raise APIError("Cette carte a été supprimée.", 404)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    data = request.get_json(silent=True) or {}
    for field in ('name', 'email', 'title', 'phone', 'website', 'instagram', 'linkedin',
                  'trade', 'service_zone', 'bio', 'google_review_url', 'facebook_url',
                  'whatsapp_number'):
        if field in data:
            setattr(card, field, data[field])
    commit_session("Impossible de mettre à jour la carte.")
    return jsonify({'message': 'Carte mise à jour.'})


@cards_bp.route('/<string:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    card.is_deleted = True
    commit_session("Impossible de supprimer la carte.")
    return jsonify({'message': 'Carte supprimée.'})


# ── Scans ─────────────────────────────────────────────────────────────────────

@cards_bp.route('/<string:card_id>/scan', methods=['POST'])
def record_scan(card_id):
    """Enregistre un scan de carte. Endpoint public (appelé à chaque vue QR)."""
    card = get_or_404(Card, card_id)
    if card.is_deleted or not card.is_active:
        raise APIError("Carte non disponible.", 404)
    scan = ScanEvent(
        card_id=card_id,
        ip_address=request.remote_addr,
        user_agent=(request.headers.get('User-Agent') or '')[:300],
    )
    db.session.add(scan)
    commit_session("Impossible d'enregistrer le scan.")
    return jsonify({'message': 'Scan enregistré.'}), 201


@cards_bp.route('/<string:card_id>/scans', methods=['GET'])
@login_required
def get_scan_stats(card_id):
    """Retourne les statistiques de scans pour le propriétaire de la carte."""
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    query = ScanEvent.query.filter_by(card_id=card_id).order_by(ScanEvent.scanned_at.desc())
    return jsonify(paginate_query(query))


# ── Galerie photos ─────────────────────────────────────────────────────────────

@cards_bp.route('/<string:card_id>/photos', methods=['GET'])
def get_photos(card_id):
    """Liste les photos d'une carte (public)."""
    card = get_or_404(Card, card_id)
    if card.is_deleted:
        raise APIError("Carte non disponible.", 404)
    photos = Photo.query.filter_by(card_id=card_id).order_by(Photo.created_at).all()
    return jsonify([p.serialize() for p in photos])


@cards_bp.route('/<string:card_id>/photos', methods=['POST'])
@login_required
def upload_photo(card_id):
    """Upload une photo avant/après pour la galerie."""
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    if 'photo' not in request.files:
        raise APIError("Aucun fichier fourni.", 400)
    file = request.files['photo']
    if not file.filename:
        raise APIError("Aucun fichier sélectionné.", 400)

    ext = os.path.splitext(secure_filename(file.filename))[1].lstrip('.').lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise APIError("Format non supporté. Utilisez JPG, PNG ou WebP.", 400)

    photo_type = request.form.get('photo_type', 'after')
    if photo_type not in ('before', 'after'):
        photo_type = 'after'
    caption = (request.form.get('caption') or '')[:200]

    unique_filename = f"card_{card_id}_{uuid.uuid4().hex}.{ext}"
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_filename))

    photo = Photo(
        card_id=card_id,
        filename=unique_filename,
        caption=caption or None,
        photo_type=photo_type,
    )
    db.session.add(photo)
    commit_session("Impossible d'enregistrer la photo.")
    return jsonify({'message': 'Photo ajoutée.', 'id': photo.id, 'filename': unique_filename}), 201


@cards_bp.route('/<string:card_id>/photos/<int:photo_id>', methods=['DELETE'])
@login_required
def delete_photo(card_id, photo_id):
    """Supprime une photo de la galerie."""
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    photo = get_or_404(Photo, photo_id)
    if photo.card_id != card_id:
        raise APIError("Non autorisé.", 403)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos', photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(photo)
    commit_session("Impossible de supprimer la photo.")
    return jsonify({'message': 'Photo supprimée.'})


# ── Demandes de soumission ─────────────────────────────────────────────────────

@cards_bp.route('/<string:card_id>/quote', methods=['POST'])
def request_quote(card_id):
    """Envoie une demande de soumission au professionnel. Endpoint public."""
    card = get_or_404(Card, card_id)
    if card.is_deleted or not card.is_active:
        raise APIError("Carte non disponible.", 404)

    data = request.get_json(silent=True) or {}
    requester_name = (data.get('name') or '').strip()
    requester_email = (data.get('email') or '').strip()
    requester_phone = (data.get('phone') or '').strip()
    message = (data.get('message') or '').strip()

    if not requester_name or not requester_email:
        raise APIError("Nom et courriel sont requis.", 400)

    quote = QuoteRequest(
        card_id=card_id,
        requester_name=requester_name,
        requester_email=requester_email,
        requester_phone=requester_phone or None,
        message=message or None,
    )
    db.session.add(quote)
    commit_session("Impossible d'enregistrer la demande.")

    pro = db.session.get(User, card.user_id)
    send_quote_notification_email(
        to_email=pro.email,
        pro_name=card.name,
        requester_name=requester_name,
        requester_email=requester_email,
        requester_phone=requester_phone,
        message=message,
        api_key=current_app.config.get('SENDGRID_API_KEY'),
        from_email=current_app.config.get('FROM_EMAIL', 'noreply@cartepro.ca'),
    )
    return jsonify({'message': 'Demande de soumission envoyée.'}), 201


@cards_bp.route('/<string:card_id>/quotes', methods=['GET'])
@login_required
def list_quotes(card_id):
    """Liste les demandes de soumission reçues pour une carte (propriétaire uniquement)."""
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        raise APIError("Non autorisé.", 403)
    query = QuoteRequest.query.filter_by(card_id=card_id).order_by(QuoteRequest.created_at.desc())
    return jsonify(paginate_query(query))
