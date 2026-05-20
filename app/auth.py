# app/auth.py

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from .models import db, User
from .extensions import limiter
from .errors import commit_session, APIError

ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MIN_PASSWORD_LENGTH = 8

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Nom d'utilisateur, courriel et mot de passe requis."}), 400

    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": f"Le mot de passe doit contenir au moins {MIN_PASSWORD_LENGTH} caractères."}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Un compte avec ce nom d'utilisateur ou courriel existe déjà."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    commit_session("Impossible de créer le compte.")

    return jsonify({"message": f"Compte '{username}' créé avec succès."}), 201

@auth_routes.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Nom d'utilisateur et mot de passe requis."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiants invalides."}), 401

    login_user(user)

    return jsonify({"message": "Connexion réussie."})

@auth_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Déconnexion réussie."})

@auth_routes.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(current_user.serialize())


@auth_routes.route('/me', methods=['PATCH'])
@login_required
def update_me():
    data = request.form or request.get_json(silent=True) or {}
    current_user.username = data.get('username', current_user.username)
    current_user.email = data.get('email', current_user.email)
    commit_session("Impossible de mettre à jour le profil.")
    return jsonify(current_user.serialize())


@auth_routes.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni.'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné.'}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1].lstrip('.').lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise APIError("Format de fichier non supporté. Utilisez JPG, PNG ou WebP.", 400)

    unique_filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_filename))

    current_user.avatar_filename = unique_filename
    commit_session("Impossible de sauvegarder l'avatar.")
    return jsonify({'message': 'Avatar mis à jour.', 'avatar': unique_filename})


@auth_routes.route('/me', methods=['DELETE'])
@login_required
def delete_me():
    current_user.username = f'deleted-{current_user.id}'
    current_user.email = f"deleted-{current_user.id}@example.com"
    current_user.set_password(os.urandom(32).hex())
    commit_session("Impossible de supprimer le compte.")
    logout_user()
    return jsonify({'message': 'Compte supprimé.'})

