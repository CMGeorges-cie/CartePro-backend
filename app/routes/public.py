from flask import Blueprint, render_template
from app.errors import get_or_404
from app.models import Card

public_bp = Blueprint('main', __name__)

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/view/<int:card_id>')
def view_card(card_id):
    card = get_or_404(Card, card_id)
    return render_template('view_card.html', card=card)


@public_bp.route('/health')
def health():
    return {'status': 'ok'}
