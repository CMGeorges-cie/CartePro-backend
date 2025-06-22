# app/routes.py
from flask import Blueprint, request, jsonify, send_file, render_template
from .models import db, Card
from .services import generate_qr_code_with_logo

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return jsonify({"message": "QR Card API is running."})

@main_routes.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' in request."}), 400

    image_buffer = generate_qr_code_with_logo(url)
    if not image_buffer:
        return jsonify({"error": "Failed to generate QR code"}), 500
        
    return send_file(image_buffer, mimetype='image/png')

# TODO: when post new card response is not found 
@main_routes.route('/cards', methods=['POST'])
def create_card():
    data = request.json
    required = ["name", "email", "title"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_card = Card(
        name=data['name'],
        email=data['email'],
        title=data['title'],
        phone=data.get('phone'),
        website=data.get('website'),
        instagram=data.get('instagram'),
        linkedin=data.get('linkedin')
    )
    db.session.add(new_card)
    db.session.commit()
    
    return jsonify({"message": "Card created successfully", "id": new_card.id}), 201

@main_routes.route('/cards/<string:card_id>', methods=['GET'])
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify({
        "id": card.id, "name": card.name, "title": card.title, "email": card.email,
        "phone": card.phone, "website": card.website, "instagram": card.instagram, "linkedin": card.linkedin
    })

@main_routes.route('/cards/<string:card_id>', methods=['PUT'])
def update_card(card_id):
    card = Card.query.get_or_404(card_id)
    data = request.json
    for key, value in data.items():
        if hasattr(card, key):
            setattr(card, key, value)
    db.session.commit()
    return jsonify({"message": "Card updated successfully"})

@main_routes.route('/cards/<string:card_id>', methods=['DELETE'])
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted successfully"})

@main_routes.route('/view/<string:card_id>', methods=['GET'])
def view_card(card_id):
    card = Card.query.get_or_404(card_id)
    return render_template('card_template.html', card=card)