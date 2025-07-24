# app/auth.py

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import db, User

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email and password required."}), 400

    # Vérifie si l'utilisateur existe déjà dans la base de données
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists."}), 400

    # Crée un nouvel utilisateur et hashe son mot de passe
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User '{username}' registered successfully."}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    login_user(user)  # <-- C'est ça qui gère la session Flask-Login

    return jsonify({"message": "Login successful."})

@auth_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."})

@auth_routes.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(current_user.serialize())


@auth_routes.route('/me', methods=['PATCH'])
@login_required
def update_me():
    data = request.form or request.json or {}
    current_user.username = data.get('username', current_user.username)
    current_user.email = data.get('email', current_user.email)
    db.session.commit()
    return jsonify(current_user.serialize())


@auth_routes.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    file.save(path)
    current_user.avatar_filename = filename
    db.session.commit()
    return jsonify({'message': 'Avatar uploaded', 'avatar': filename})


@auth_routes.route('/me', methods=['DELETE'])
@login_required
def delete_me():
    current_user.username = f'deleted-{current_user.id}'
    current_user.email = f"deleted-{current_user.id}@example.com"
    current_user.password_hash = ''
    db.session.commit()
    logout_user()
    return jsonify({'message': 'Account deleted'})

