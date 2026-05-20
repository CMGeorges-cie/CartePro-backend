from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required, current_user
import stripe
import datetime
from app.models import db, Subscription, User
from app.errors import APIError, commit_session

stripe_bp = Blueprint('stripe', __name__)


@stripe_bp.route('/config', methods=['GET'])
@login_required
def stripe_config():
    """Retourne la clé publique Stripe et les plans disponibles."""
    return jsonify({
        'publicKey': current_app.config.get('STRIPE_PUBLIC_KEY'),
        'plans': {
            'monthly': {
                'price_id': current_app.config.get('STRIPE_MONTHLY_PRICE_ID'),
                'amount': 1500,
                'currency': 'cad',
                'interval': 'month',
                'label': '15 $/mois',
            },
            'annual': {
                'price_id': current_app.config.get('STRIPE_ANNUAL_PRICE_ID'),
                'amount': 12000,
                'currency': 'cad',
                'interval': 'year',
                'label': '120 $/an',
            },
        },
    })


@stripe_bp.route('/create-checkout', methods=['POST'])
@login_required
def create_checkout():
    """Crée une session Stripe Checkout pour souscrire au plan mensuel ou annuel."""
    data = request.get_json(silent=True) or {}
    plan = data.get('plan', 'monthly')
    if plan not in ('monthly', 'annual'):
        raise APIError("Plan invalide. Choisissez 'monthly' ou 'annual'.", 400)

    price_key = 'STRIPE_MONTHLY_PRICE_ID' if plan == 'monthly' else 'STRIPE_ANNUAL_PRICE_ID'
    price_id = current_app.config.get(price_key)
    if not price_id:
        raise APIError("Ce plan de paiement n'est pas configuré.", 503)

    customer_id = current_user.stripe_customer_id
    if not customer_id:
        try:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={'user_id': current_user.id},
            )
            customer_id = customer.id
            current_user.stripe_customer_id = customer_id
            commit_session("Impossible de créer le client Stripe.")
        except stripe.StripeError:
            raise APIError("Impossible de créer le client Stripe.", 502)

    app_url = current_app.config.get('APP_URL', 'http://localhost:3000')
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f"{app_url}/abonnement/succes?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{app_url}/abonnement/annule",
        )
    except stripe.StripeError:
        raise APIError("Impossible de créer la session de paiement.", 502)

    return jsonify({'checkout_url': session.url})


@stripe_bp.route('/portal', methods=['GET'])
@login_required
def customer_portal():
    """Redirige vers le portail de gestion d'abonnement Stripe."""
    if not current_user.stripe_customer_id:
        raise APIError("Aucun abonnement associé à ce compte.", 404)
    app_url = current_app.config.get('APP_URL', 'http://localhost:3000')
    try:
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=f"{app_url}/compte",
        )
    except stripe.StripeError:
        raise APIError("Impossible d'accéder au portail de facturation.", 502)
    return jsonify({'portal_url': session.url})


@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    try:
        if current_app.config.get("TESTING"):
            event = request.get_json(silent=True) or {}
        elif not webhook_secret:
            raise APIError("Webhook Stripe non configuré.", 500)
        elif not sig_header:
            raise APIError("Signature Stripe manquante.", 400)
        else:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except APIError:
        raise
    except stripe.SignatureVerificationError:
        raise APIError("Signature Stripe invalide.", 400)
    except ValueError:
        raise APIError("Payload webhook invalide.", 400)
    except stripe.StripeError:
        raise APIError("Impossible de valider le webhook Stripe.", 502)

    event_type = event.get('type') if isinstance(event, dict) else event['type']
    data_obj = (event.get('data', {}).get('object', {})
                if isinstance(event, dict) else event['data']['object'])

    if event_type == 'customer.subscription.updated':
        sub = Subscription.query.filter_by(stripe_subscription_id=data_obj.get('id')).first()
        if sub:
            sub.status = data_obj.get('status', sub.status)
            commit_session("Impossible de mettre à jour l'abonnement.")

    elif event_type == 'customer.subscription.created':
        customer_id = data_obj.get('customer')
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            sub = Subscription(
                user_id=user.id,
                plan_name=data_obj.get('plan', {}).get('id', ''),
                stripe_subscription_id=data_obj.get('id'),
                status=data_obj.get('status', 'active'),
                current_period_end=datetime.datetime.fromtimestamp(
                    data_obj.get('current_period_end', 0)
                ),
            )
            db.session.add(sub)
            commit_session("Impossible de créer l'abonnement.")

    elif event_type == 'customer.subscription.deleted':
        sub = Subscription.query.filter_by(stripe_subscription_id=data_obj.get('id')).first()
        if sub:
            sub.status = 'canceled'
            commit_session("Impossible d'annuler l'abonnement.")

    return jsonify({'status': 'success'})
