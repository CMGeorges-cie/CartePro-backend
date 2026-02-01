#__init__.py
from flask import Flask, render_template
from flask_wtf import CSRFProtect
from loguru import logger
from flask_cors import CORS
from .auth import auth_routes
from .routes.cards import cards_bp
from .routes.admin import admin_bp
from .routes.stripe import stripe_bp
from .routes.qr import qr_bp
from .routes.public import public_bp
from .admin import admin
from .models import User
from .extensions import db, login_manager, limiter
import os
import stripe
from dotenv import load_dotenv
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .health import health_bp


load_dotenv()


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory."""

    env = os.environ.get("FLASK_ENV")

    # Détermination automatique de la configuration si celle par défaut est utilisée
    if config_class is Config:
        if env == "production":
            config_class = ProductionConfig
        elif env == "testing":
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    app = Flask(__name__, instance_relative_config=True, template_folder=template_path)
    app.config.from_object(config_class)
    app.register_blueprint(health_bp)

    # Dossier instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = app.config['SECRET_KEY']
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    log_file = os.path.join(app.instance_path, 'app.log')
    logger.add(log_file)

    # Initialisation des extensions
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    db.init_app(app)
    CSRFProtect(app)
    CORS(app)
    admin.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    limiter.init_app(app)

    # Blueprints
    def register_routes(app):
        app.register_blueprint(auth_routes, url_prefix='/auth')
        app.register_blueprint(cards_bp, url_prefix='/api/v1/cards')
        app.register_blueprint(qr_bp, url_prefix='/api/v1/qr')
        app.register_blueprint(stripe_bp, url_prefix='/api/v1/stripe')
        app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
        app.register_blueprint(public_bp)  # index, /view/:id, etc.

    register_routes(app)                                    # Routes API

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Gestion des erreurs
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Server error: %s", error)
        return render_template('errors/500.html'), 500

    # Création DB
    with app.app_context():
        db.create_all()

    return app
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  