# app/__init__.py
from flask import Flask, render_template
from flask_cors import CORS
from .routes import main_routes
from .auth import auth_routes
from config import Config
import os
from .admin import admin
from .models import User
from flask_sqlalchemy import SQLAlchemy
from .extensions import db, login_manager
import stripe



def create_app(config_class=Config):
    # Chemin absolu vers templates
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Assurer que le dossier 'instance' existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialiser les extensions
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = app.config['SECRET_KEY']  # Utiliser la clé secrète de la config
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    
    # Configurer Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']


    
    db.init_app(app)
    CORS(app)
    admin.init_app(app) # Initialiser Flask-Admin
    login_manager.init_app(app)  # Initialiser Flask-Login
    login_manager.login_view = 'auth.login'  # Définir la vue de connexion

    # Enregistrer le blueprint
    app.register_blueprint(main_routes, url_prefix='/api/v1')
    app.register_blueprint(auth_routes, url_prefix='/auth')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    #gestion erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        # On retourne notre template personnalisé et le code 404
        return render_template('errors/404.html'), 404


    # Créer les tables de la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()
        # Optionnel : Créer un utilisateur admin par défaut
        
    return app

app = create_app()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          