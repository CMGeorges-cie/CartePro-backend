from flask import Blueprint, request, send_file, jsonify
from app.services import generate_qr_code_with_logo
from app.extensions import limiter

qr_bp = Blueprint('qr', __name__)


@qr_bp.route('/generate', methods=['POST'])
@limiter.limit("20 per minute")
def generate_qr():
    """Génère un QR code PNG. Limité à 20 requêtes/min par IP."""
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL requise."}), 400
    buf = generate_qr_code_with_logo(url)
    if not buf:
        return jsonify({"error": "Échec de la génération du QR code."}), 500
    return send_file(buf, mimetype='image/png')
