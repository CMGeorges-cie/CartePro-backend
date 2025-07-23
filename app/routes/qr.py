from flask import Blueprint, request, send_file, jsonify
from app.services import generate_qr_code_with_logo

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400
    buf = generate_qr_code_with_logo(url)
    if not buf:
        return jsonify({"error": "QR generation failed"}), 500
    return send_file(buf, mimetype='image/png')