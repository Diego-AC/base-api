from functools import wraps

import jwt
from flask import current_app, g, request
from werkzeug.exceptions import Unauthorized


def login_required(f):
    """Decodifica JWT HS256 usando SECRET_KEY del config y expone el payload en g."""
    @wraps(f)
    def auth(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized('Missing authorization header')

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise Unauthorized('Invalid authorization header format')

        secret = current_app.config.get('SECRET_KEY')
        if not secret:
            raise Unauthorized('Server secret not configured')

        try:
            payload = jwt.decode(parts[1], secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise Unauthorized('Token expired')
        except jwt.InvalidTokenError:
            raise Unauthorized('Invalid token')

        g.current_user_id = payload.get('user_id')
        g.jwt_payload = payload

        return f(*args, **kwargs)
    return auth
