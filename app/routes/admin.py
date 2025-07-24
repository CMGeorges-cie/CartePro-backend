# routes/admin.py
from flask import Blueprint, jsonify, request
from app.models import User, Card, db
from app.decorators import admin_required
from app.utils import paginate_query, paginate_list
import os

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    return jsonify(paginate_query(User.query))
    email = request.args.get('email')
    query = User.query
    if email:
        query = query.filter_by(email=email)
    users = query.all()
    return jsonify([user.serialize() for user in users])

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


@admin_bp.route('/restore_card/<string:card_id>', methods=['POST'])
@admin_required
def restore_card(card_id):
    card = Card.query.get_or_404(card_id)
    card.is_deleted = False
    db.session.commit()
    return jsonify({'message': 'Card restored'})


@admin_bp.route('/export', methods=['GET'])
@admin_required
def export_data():
    model = request.args.get('model', 'users')
    fmt = request.args.get('format', 'json')
    if model == 'cards':
        data = [c.serialize() for c in Card.query.all()]
    else:
        data = [u.serialize() for u in User.query.all()]
    if fmt == 'csv':
        import csv
        from io import StringIO
        si = StringIO()
        if data:
            writer = csv.DictWriter(si, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return si.getvalue(), 200, {'Content-Type': 'text/csv'}
    return jsonify(data)

