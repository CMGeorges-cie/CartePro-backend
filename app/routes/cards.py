from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Card, db

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/', methods=['POST'])
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

@cards_bp.route('/<string:card_id>', methods=['GET'])
@login_required
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(card.serialize())

@cards_bp.route('/<string:card_id>', methods=['PUT'])
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

@cards_bp.route('/<string:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Card deleted'})

