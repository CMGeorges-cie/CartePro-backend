# app/routes.py
from flask import Blueprint, request, jsonify, send_file, render_template, redirect, current_app
from .models import  Card
from .services import generate_qr_code_with_logo
import stripe
# Assurez-vous d'avoir installé stripe avec `pip install stripe`



# Dictionnaire de nos "Price IDs" que tu vas créer dans ton tableau de bord Stripe
#STRIPE_PRICES = {
 #   'one_time': 'price_1Rcxsq00padFPyonZ4wx7Sdd', # Remplace par ton Price ID Stripe
 #   'pro_annual': 'price_1RcxxJ00padFPyonY8Jc8jtK'
# }

main_routes = Blueprint('main', __name__)

@main_routes.route('/create-checkout-session', methods=['POST'])
# @login_required # <-- On protégera cette route plus tard
def create_checkout_session():
    data = request.json
    price_id = data.get('price_id') # <-- On reçoit le price_id

    if not price_id:
        return jsonify({"error": "Missing price_id"}), 400

    try:
        # On vérifie que le prix existe et est actif pour plus de sécurité
        price = stripe.Price.retrieve(price_id)
        if not price.active:
            return jsonify({"error": "This price is no longer available"}), 400

        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription' if price.type == 'recurring' else 'payment',
            success_url=request.host_url + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'payment-cancel',
        )
        # On retourne l'URL de checkout au lieu de rediriger directement,
        # c'est plus propre pour une API.
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500

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


@main_routes.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    # webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e: # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e: # Invalid signature
        return 'Invalid signature', 400

    # TODO: Gérer l'événement checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Le paiement a réussi !
        # Ici, tu vas chercher le user_id, et mettre à jour sa souscription dans la DB.
        # Ex: créer une nouvelle entrée dans la table Subscription,
        # ou mettre à jour la carte avec plan_type = 'one_time'.
        print(f"Payment successful for session: {session.id}")

    # TODO:Gérer d'autres événements...
    
    return 'Success', 200


@main_routes.route('/config', methods=['GET'])
def get_config():
    # On récupère tous les produits actifs depuis Stripe
    #print("Stripe API KEY:", stripe.api_key)  # DEBUG
    # L'argument 'expand' permet de récupérer le prix par défaut en une seule requête
    products = stripe.Product.list(active=True, expand=['data.default_price'])
    
    plans = []
    for product in products:
        # On s'assure que le produit a bien un prix par défaut
        if product.default_price:
            plans.append({
                "name": product.name,
                "description": product.description,
                "price_id": product.default_price.id,
                # Le prix est en centimes, on le convertit en dollars
                "price": f"{product.default_price.unit_amount / 100:.2f}", 
                "currency": product.default_price.currency,
                "interval": product.default_price.recurring.interval if product.default_price.recurring else 'one-time',
            })

    return jsonify(plans)