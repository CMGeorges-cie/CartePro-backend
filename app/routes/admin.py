# routes/admin.py
from flask import Blueprint, jsonify, request
from app.models import User, Card
from app.decorators import admin_required
from app.utils import paginate_query, paginate_list
from app.extensions import db
import os

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    email = request.args.get('email')
    query = User.query
    if email:
        query = query.filter(User.email.like(f"%{email}%"))
    return jsonify(paginate_query(query))

@admin_bp.route('/cards', methods=['GET'])
@admin_required
def list_all_cards():
    return jsonify(paginate_query(Card.query))

@admin_bp.route('/backups', methods=['GET'])
@admin_required
def list_backups():
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        return jsonify(paginate_list([]))
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.enc')]
    return jsonify(paginate_list(backups))

@admin_bp.route('/restore/<filename>', methods=['POST'])
@admin_required
def restore_backup(filename):
    backup_dir = os.path.join(os.getcwd(), 'backups')
    file_path = os.path.join(backup_dir, filename)
    if not os.path.exists(file_path) or not filename.endswith('.enc'):
        return jsonify({'error': 'Backup file not found'}), 404
    # Logique de restauration à adapter
    return jsonify({'message': f'Backup {filename} restored (simulation).'})


@admin_bp.route('/users/<int:user_id>/restore', methods=['POST'])
@admin_required
def restore_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user.is_deleted:
        return jsonify({'message': 'User not deleted'}), 400
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    if not username or not email:
        return jsonify({'error': 'username and email required'}), 400
    user.username = username
    user.email = email
    user.is_deleted = False
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': f'User {user_id} restored'})

