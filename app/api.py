from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Card, db
from app.decorators import admin_required

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ------------------ CRUD CARDS ------------------

# Ressource : Créer une carte professionnelle
@api_bp.route('/cards', methods=['POST'])
@login_required
def create_card():
    data = request.json
    card = Card(
        user_id=current_user.id,
        name=data.get('name'),
        email=data.get('email'),
        title=data.get('title'),
        phone=data.get('phone'),
        website=data.get('website'),
        instagram=data.get('instagram'),
        linkedin=data.get('linkedin')
    )
    db.session.add(card)
    db.session.commit()
    return jsonify({'message': 'Card created', 'id': card.id}), 201

# Ressource : Lire une carte professionnelle (propriétaire seulement)
@api_bp.route('/cards/<int:card_id>', methods=['GET'])
@login_required
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(card.serialize())

# Ressource : Modifier une carte professionnelle (propriétaire seulement)
@api_bp.route('/cards/<int:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    card.name = data.get('name', card.name)
    card.email = data.get('email', card.email)
    card.title = data.get('title', card.title)
    card.phone = data.get('phone', card.phone)
    card.website = data.get('website', card.website)
    card.instagram = data.get('instagram', card.instagram)
    card.linkedin = data.get('linkedin', card.linkedin)
    db.session.commit()

    return jsonify({'message': 'Card updated'})

# Ressource : Supprimer une carte professionnelle (propriétaire seulement)
@api_bp.route('/cards/<int:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Card deleted'})

# ------------------ ADMIN ROUTES ------------------

# Ressource : Liste des utilisateurs (admin)
@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def list_users():
    from app.models import User
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

# Ressource : Liste de toutes les cartes (admin)
@api_bp.route('/admin/cards', methods=['GET'])
@admin_required
def list_all_cards():
    cards = Card.query.all()
    return jsonify([card.serialize() for card in cards])

# Ressource : Liste des fichiers de sauvegarde chiffrés (admin)
@api_bp.route('/admin/backups', methods=['GET'])
@admin_required
def list_backups():
    import os
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        return jsonify([])
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.enc')]
    return jsonify(backups)
