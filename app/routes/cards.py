from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Card, db
from app.errors import APIError, commit_session, get_or_404
from app.utils import paginate_query

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/', methods=['GET'])
@login_required
def list_cards():
    query = Card.query.filter_by(user_id=current_user.id)
    return jsonify(paginate_query(query))

@cards_bp.route('/', methods=['POST'])
@login_required
def create_card():
    """
    Create Business Card

    -tags:
        - Cards
    parameters:
        - in: body 
            name: card
            description: Card details
            schema:
                type: object
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
    responses:
        201:
            description: Card created
        403:
            description: Card limit reached (for non-pro users)
    security:
        - bearerAuth: []
         
    """

    data = request.get_json(silent=True) or {}
    if not current_user.is_pro and Card.query.filter_by(user_id=current_user.id).count() >= 1:
        return jsonify({'error': 'Card limit reached'}), 403
    if not data.get('name') or not data.get('email') or not data.get('title'):
        raise APIError("Name, email and title are required.", 400)
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
    commit_session("Unable to create card.")
    return jsonify({'message': 'Card created', 'id': card.id}), 201

@cards_bp.route('/<string:card_id>', methods=['GET'])
@login_required
def get_card(card_id):
   
    card = get_or_404(Card, card_id)
    if card.is_deleted:
        return jsonify({'error': 'Deleted'}), 403
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(card.serialize())

@cards_bp.route('/<string:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    
    card = get_or_404(Card, card_id)
    if card.is_deleted:
        return jsonify({'error': 'Deleted'}), 403
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json(silent=True) or {}
    card.name = data.get('name', card.name)
    card.email = data.get('email', card.email)
    card.title = data.get('title', card.title)
    card.phone = data.get('phone', card.phone)
    card.website = data.get('website', card.website)
    card.instagram = data.get('instagram', card.instagram)
    card.linkedin = data.get('linkedin', card.linkedin)
    commit_session("Unable to update card.")
    return jsonify({'message': 'Card updated'})

@cards_bp.route('/<string:card_id>', methods=['DELETE'])
@login_required
def delete_card(card_id):
   
    card = get_or_404(Card, card_id)
    if card.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    card.is_deleted = True
    commit_session("Unable to delete card.")
    return jsonify({'message': 'Card deleted'})

