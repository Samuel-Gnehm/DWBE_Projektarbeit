from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/')
def index():
    return 'Auth-Blueprint – Platzhalter Phase 1', 200
