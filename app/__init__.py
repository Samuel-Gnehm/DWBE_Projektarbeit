import os
from pathlib import Path
from dotenv import load_dotenv

# .env laden BEVOR config importiert wird, da Klassenattribute beim Import ausgewertet werden
_env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=_env_path)

from flask import Flask, render_template

from .config import config
from .extensions import db, login_manager, migrate, csrf, jwt


def create_app(config_name='development'):
    app = Flask(__name__)

    # Konfiguration laden
    app.config.from_object(config[config_name])

    # Extensions initialisieren
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    jwt.init_app(app)

    # JWT-Fehler-Handler (geben JSON statt HTML zurück)
    from flask import jsonify

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'error': 'Kein Token vorhanden oder ungültig'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token abgelaufen'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Ungültiger Token'}), 422

    # Modelle importieren, damit Flask-Migrate sie erkennt
    with app.app_context():
        from . import models  # noqa: F401

    # Blueprints registrieren
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.api import api_bp
    from .blueprints.provider import provider_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)
    app.register_blueprint(provider_bp, url_prefix='/provider')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Fehler-Handler
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # Globaler Template-Kontext: active_ride für Navbar-Anzeige
    @app.context_processor
    def inject_active_ride():
        from flask_login import current_user
        active_ride = None
        if current_user.is_authenticated and current_user.user_rolle == 'user':
            from app.models.ride import Ride
            active_ride = Ride.query.filter_by(
                rider_uid=current_user.uid, endzeit=None
            ).first()
        return dict(active_ride=active_ride)

    return app
