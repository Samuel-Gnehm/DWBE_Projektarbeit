from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if current_user.user_rolle != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


admin_required    = role_required('admin')
provider_required = role_required('provider')
rider_required    = role_required('user')
