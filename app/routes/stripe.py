from flask import Blueprint, jsonify, current_app, request
import stripe
import datetime
from app.models import db, Subscription, User
from app.errors import APIError, commit_session

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
    except stripe.StripeError:
        raise APIError("Unable to load Stripe configuration.", 502)


@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    try:
        if current_app.config.get("TESTING"):
            event = request.get_json(silent=True) or {}
        elif not webhook_secret:
            raise APIError("Stripe webhook is not configured.", 500)
        elif not sig_header:
            raise APIError("Missing Stripe signature.", 400)
        else:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except APIError:
        raise
    except stripe.SignatureVerificationError:
        raise APIError("Invalid Stripe signature.", 400)
    except ValueError:
        raise APIError("Invalid webhook payload.", 400)
    except stripe.StripeError:
        raise APIError("Unable to validate Stripe webhook.", 502)

    if event['type'] == 'customer.subscription.updated':
        data = event['data']['object']
        sub = Subscription.query.filter_by(stripe_subscription_id=data['id']).first()
        if sub:
            sub.status = data['status']
            commit_session("Unable to update subscription.")
    elif event['type'] == 'customer.subscription.created':
        data = event['data']['object']
        customer_id = data['customer']
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            sub = Subscription(
                user_id=user.id,
                plan_name=data.get('plan', {}).get('id', ''),
                stripe_subscription_id=data['id'],
                status=data['status'],
                current_period_end=datetime.datetime.fromtimestamp(data['current_period_end'])
            )
            db.session.add(sub)
            commit_session("Unable to create subscription.")
    return jsonify({'status': 'success'})
