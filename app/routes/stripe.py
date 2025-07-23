from flask import Blueprint, jsonify, current_app
import stripe

stripe_bp = Blueprint('stripe', __name__)

@stripe_bp.route('/config', methods=['GET'])
def stripe_config():
    # Retourne la config Stripe (clé publique, plans, etc.)
    public_key = current_app.config.get('STRIPE_PUBLIC_KEY')
    try:
        products = stripe.Product.list(limit=5)
        prices = stripe.Price.list(limit=5)
        return jsonify({
            "publicKey": public_key,
            "products": [p for p in products.data],
            "prices": [p for p in prices.data]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500