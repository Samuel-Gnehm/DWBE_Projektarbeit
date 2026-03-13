from functools import wraps

from flask import abort
from flask_login import current_user


def provider_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.user_rolle != 'provider':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def rider_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.user_rolle != 'user':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.user_rolle != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated
