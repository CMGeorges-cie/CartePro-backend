# app/__init__.py
from flask import Flask, render_template
from flask_cors import CORS
from .models import db
from .routes import main_routes
from .auth import auth_routes
from config import Config
import os
from .admin import admin

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Assurer que le dossier 'instance' existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialiser les extensions
    db.init_app(app)
    CORS(app)
    admin.init_app(app) # Initialiser Flask-Admin

    # Enregistrer le blueprint
    app.register_blueprint(main_routes)
    # Tu pourras ajouter ton blueprint d'authentification ici plus tard
    # from .auth import auth_routes
    # app.register_blueprint(auth_routes)
    app.register_blueprint(auth_routes, url_prefix='/auth')


    #gestion erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        # On retourne notre template personnalisé et le code 404
        return render_template('errors/404.html'), 404


    # Créer les tables de la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app