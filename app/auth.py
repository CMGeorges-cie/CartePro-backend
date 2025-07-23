# app/auth.py

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
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
    return jsonify({"id": current_user.id, "username": current_user.username})

