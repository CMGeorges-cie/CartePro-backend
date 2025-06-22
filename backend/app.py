# backend/app.py
from flask import Flask, request, send_file
from flask import Flask, request, send_file, jsonify
import qrcode
from PIL import Image
import io
import os

app = Flask(__name__)


# Configurations
UPLOAD_FOLDER = 'uploads'
DEFAULT_LOGO = 'static/logo.png'
DATA_FILE = 'data/cards.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Helper to load cards data
def load_cards():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Helper to save cards data
def save_cards(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return jsonify({"message": "QR Code Generator API is running."})

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' in request."}), 400

    logo_path = DEFAULT_LOGO
    if 'logo_path' in data and os.path.exists(data['logo_path']):
        logo_path = data['logo_path']

    try:
        # Generate QR code
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Add logo
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            basewidth = 60
            wpercent = basewidth / float(logo.size[0])
            hsize = int(float(logo.size[1]) * wpercent)
            logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos)

        # Save image to buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create_card', methods=['POST'])
def create_card():
    data = request.json
    required_fields = ["name", "email", "title"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields: name, email, title"}), 400

    cards = load_cards()
    card_id = str(uuid.uuid4())

    card_data = {
        "id": card_id,
        "name": data["name"],
        "email": data["email"],
        "title": data["title"],
        "phone": data.get("phone", ""),
        "website": data.get("website", ""),
        "instagram": data.get("instagram", ""),
        "linkedin": data.get("linkedin", "")
    }

    cards[card_id] = card_data
    save_cards(cards)

    return jsonify({"message": "Card created successfully", "id": card_id}), 201

@app.route('/card/<card_id>', methods=['GET'])
def get_card(card_id):
    cards = load_cards()
    card = cards.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404
    return jsonify(card)


if __name__ == '__main__':
    # IMPORTANT: Use os.environ.get("PORT") and bind to '0.0.0.0'
    port = int(os.environ.get("PORT", 5000)) # Default to 5000 for local testing
    app.run(host='0.0.0.0', port=port, debug=False)  # Set debug=True for development, change to False in production
   # app.run(debug=True)
