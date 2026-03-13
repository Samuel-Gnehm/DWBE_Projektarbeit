from flask import Blueprint

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return 'E-Scooter Verleih – Phase 1 läuft.', 200
