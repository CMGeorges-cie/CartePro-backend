# routes/admin.py
from flask import Blueprint, jsonify, request
from app.models import User, Card
from app.decorators import admin_required
import os

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@admin_bp.route('/cards', methods=['GET'])
@admin_required
def list_all_cards():
    cards = Card.query.all()
    return jsonify([card.serialize() for card in cards])

@admin_bp.route('/backups', methods=['GET'])
@admin_required
def list_backups():
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        return jsonify([])
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.enc')]
    return jsonify(backups)

@admin_bp.route('/restore/<filename>', methods=['POST'])
@admin_required
def restore_backup(filename):
    backup_dir = os.path.join(os.getcwd(), 'backups')
    file_path = os.path.join(backup_dir, filename)
    if not os.path.exists(file_path) or not filename.endswith('.enc'):
        return jsonify({'error': 'Backup file not found'}), 404
    # Logique de restauration à adapter
    return jsonify({'message': f'Backup {filename} restored (simulation).'})
