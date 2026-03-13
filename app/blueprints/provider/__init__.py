from flask import Blueprint

provider_bp = Blueprint('provider', __name__)

from . import routes  # noqa: F401, E402
