from flask import g, jsonify, current_app
from functools import wraps


def require_permission(code: str):
    def decode(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            userId = getattr(g, 'user_id', None)
            perms = getattr(g, 'perms', None)

            if not userId or perms is None:
                return jsonify({"error": "Unauthorized"}), 401
            if code not in perms:
                current_app.logger.warning(
                    f'{userId} with user no permissions')
                return jsonify({"error": "User have no permission"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decode
