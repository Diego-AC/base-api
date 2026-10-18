from typing import Optional

import jwt
from flask import Request, current_app
from werkzeug.exceptions import Unauthorized

from ..contract import AuthBackend


class JwtBackend:
    """Backend JWT.

    Valida firma, ``exp`` (si está presente) y ``nbf`` (PyJWT default).
    **NO interpreta el payload**: el dict de claims se devuelve tal cual
    está en ``g.identity`` y el fork lo lee como quiera.

    Esto significa que un token con ``payload = {}`` o ``payload = {"exp": ...}``
    es válido y se acepta igual. El fork decide qué claims emite.

    Claims que el backend NO valida por default (configuralos vía
    constructor si los necesitás):
    - ``iat``
    - ``aud`` → ``audience=...``
    - ``iss`` → ``issuer=...``

    Configuración:
    - ``secret``: callable o string. Si es ``None``, se lee de
      ``app.config['SECRET_KEY']``.
    - ``algorithm``: algoritmo de firma. Default ``"HS256"``.
    - ``audience``: si se setea, se valida el claim ``aud``.
    - ``issuer``: si se setea, se valida el claim ``iss``.
    - ``leeway``: tolerancia de reloj en segundos. Default 0.
    """

    name = "jwt"

    def __init__(
        self,
        secret=None,
        algorithm: str = "HS256",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
        leeway: int = 0,
    ):
        self._secret = secret
        self.algorithm = algorithm
        self.audience = audience
        self.issuer = issuer
        self.leeway = leeway

    def _get_secret(self) -> str:
        if self._secret is None:
            return current_app.config.get("SECRET_KEY", "")
        if callable(self._secret):
            value = self._secret()
        else:
            value = self._secret
        if not value:
            raise Unauthorized(
                "JwtBackend: no secret configured. Pass secret=... or "
                "set SECRET_KEY in your config."
            )
        return value

    def _decode_kwargs(self) -> dict:
        kwargs = {
            "algorithms": [self.algorithm],
            "leeway": self.leeway,
        }
        if self.audience is not None:
            kwargs["audience"] = self.audience
        if self.issuer is not None:
            kwargs["issuer"] = self.issuer
        return kwargs

    def can_handle(self, request: Request) -> bool:
        auth = request.headers.get("Authorization", "")
        parts = auth.split(maxsplit=1)
        return len(parts) == 2 and parts[0].lower() == "bearer"

    def authenticate(self, request: Request) -> dict:
        auth = request.headers.get("Authorization", "")
        token = auth.split(maxsplit=1)[1]

        try:
            payload = jwt.decode(
                token,
                self._get_secret(),
                **self._decode_kwargs(),
            )
        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired")
        except jwt.InvalidAudienceError:
            raise Unauthorized("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise Unauthorized("Invalid token issuer")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token")

        return payload
