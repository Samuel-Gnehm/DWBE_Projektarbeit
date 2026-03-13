import os
from pathlib import Path
from dotenv import load_dotenv

# .env laden BEVOR config importiert wird, da Klassenattribute beim Import ausgewertet werden
_env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=_env_path)

from flask import Flask

from .config import config
from .extensions import db, login_manager, migrate


def create_app(config_name='development'):
    app = Flask(__name__)

    # Konfiguration laden
    app.config.from_object(config[config_name])

    # Extensions initialisieren
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Modelle importieren, damit Flask-Migrate sie erkennt
    with app.app_context():
        from . import models  # noqa: F401

    # Blueprints registrieren
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    return app
