from flask import Blueprint, render_template
from .cards import cards_bp
from .admin import admin_bp
from .stripe import stripe_bp
from .qr import qr_bp

public_bp = Blueprint('main', __name__)

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/view/<int:card_id>')
def view_card(card_id):
    from app.models import Card
    card = Card.query.get_or_404(card_id)
    return render_template('view_card.html', card=card)


@public_bp.route('/health')
def health():
    return {'status': 'ok'}
