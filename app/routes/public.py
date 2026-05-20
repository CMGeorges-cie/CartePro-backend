from flask import Blueprint, render_template, send_from_directory, current_app
from app.errors import get_or_404
from app.models import Card
import os

public_bp = Blueprint('main', __name__)


@public_bp.route('/')
def index():
    return render_template('index.html')


@public_bp.route('/view/<string:card_id>')
def view_card(card_id):
    card = get_or_404(Card, card_id)
    return render_template('view_card.html', card=card)


@public_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Sert les fichiers uploadés localement (photos, avatars).
    En production avec S3, ce endpoint n'est pas utilisé."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)
