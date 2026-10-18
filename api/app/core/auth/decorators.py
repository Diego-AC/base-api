from functools import wraps
from typing import List

from flask import g, request
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.exceptions import Unauthorized

from .registry import get_backend


class _AuthConfigSchema(Schema):
    backends = fields.List(
        fields.String(required=True, validate=validate.Length(min=1)),
        required=True,
        validate=validate.Length(min=1),
    )
    mode = fields.String(
        validate=validate.OneOf(["any", "all"]),
        load_default="any",
    )


def _validate_config(backends: List[str], mode: str) -> None:
    try:
        _AuthConfigSchema().load({"backends": backends, "mode": mode})
    except ValidationError as e:
        if "backends" in e.messages and isinstance(e.messages["backends"], dict):
            if "length" in str(e.messages["backends"]):
                raise ValueError(
                    "@auth_required expects at least one backend. "
                    "To declare a public endpoint, omit the decorator entirely."
                ) from None
        messages = []
        for field, errors in e.messages.items():
            for err in errors:
                if isinstance(err, dict):
                    err = str(err)
                messages.append(f"{field}: {err}")
        raise ValueError(
            f"@auth_received got invalid config: {'; '.join(messages)}"
        ) from None


def auth_required(backends: List[str], mode: str = "any"):
    """Factory de decorador de autenticación.

    El fork registra sus backends con :func:`register_backend` y pasa
    los nombres (strings) a este decorador::

        from app.core.auth import auth_required

        class MyResource(BaseResource):
            @auth_required(['jwt', 'hash'])
            def get(self): ...

            @auth_required(['jwt'])
            def post(self): ...

    Reglas:
    - ``backends`` debe tener al menos un elemento. ``[]`` es un
      error (``ValueError`` al decorar): si querés un endpoint
      público, omití el decorador.
    - Si algún nombre no está registrado, la app no levanta:
      ``RegistryError`` al decorar con un mensaje que lista los
      backends disponibles.
    - ``mode='any'`` (default): el primer backend que autentique
      gana. Si ninguno autentica, ``401 Unauthorized``.
    - ``mode='all'``: todos los backends que ``can_handle()`` deban
      autenticar. Útil para escenarios donde un endpoint requiere
      múltiples credenciales.

    La identidad devuelta por el backend queda en ``flask.g.identity``
    como un dict opaco.
    """
    if not isinstance(backends, (list, tuple)):
        raise TypeError(
            f"@auth_required expects a list of backend names, "
            f"got {type(backends).__name__}"
        )
    backends = list(backends)
    _validate_config(backends, mode)

    candidates = [get_backend(name) for name in backends]

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method == "OPTIONS":
                return f(*args, **kwargs)

            required = [b for b in candidates if b.can_handle(request)]

            if not required:
                raise Unauthorized("Missing or invalid credentials")

            g.identity = None

            if mode == "any":
                last_error = Unauthorized("Invalid credentials")
                for backend in required:
                    try:
                        g.identity = backend.authenticate(request)
                        return f(*args, **kwargs)
                    except Unauthorized as e:
                        last_error = e
                raise last_error

            identities = []
            for backend in required:
                identities.append(backend.authenticate(request))
            g.identity = identities[0] if len(identities) == 1 else identities

            return f(*args, **kwargs)

        return wrapper

    return decorator
