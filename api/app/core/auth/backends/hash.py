from typing import Callable, Optional

import hmac
import hashlib
import time

from flask import Request, current_app
from werkzeug.exceptions import Unauthorized

from ..contract import AuthBackend


class HashBackend:
    """Backend de prueba lógica: api_key + timestamp + hmac.

    Header esperado::

        Authorization: Hash <api_key>:<timestamp_ms>:<signature_hex>

    ``<signature_hex>`` es ``hmac_sha256(secret, str(timestamp_ms))``.

    El backend NO sabe qué hay detrás de un api_key. La resolución
    ``api_key_str -> identity_dict`` la provee el fork vía ``resolve``.

    Si ``resolve`` devuelve ``None`` o lanza una excepción, el backend
    levanta ``Unauthorized``.

    Configuración:
    - ``secret``: callable o string. Si es ``None``, se lee de
      ``app.config['FRONTEND_SECRET']``.
    - ``resolve``: callable que recibe el api_key y devuelve un dict
      con la identidad (o ``None`` si el api_key no es válido).
    - ``validity_seconds``: ventana de tiempo. Default 10s.
    """

    name = "hash"

    def __init__(
        self,
        secret=None,
        resolve: Optional[Callable[[str], Optional[dict]]] = None,
        validity_seconds: int = 10,
    ):
        self._secret = secret
        self._resolve = resolve
        self.validity_seconds = validity_seconds

    def _get_secret(self) -> str:
        if self._secret is None:
            return current_app.config.get("FRONTEND_SECRET", "")
        if callable(self._secret):
            value = self._secret()
        else:
            value = self._secret
        if not value:
            raise Unauthorized(
                "HashBackend: no secret configured. Pass secret=... or "
                "set FRONTEND_SECRET in your config."
            )
        return value

    def can_handle(self, request: Request) -> bool:
        auth = request.headers.get("Authorization", "")
        parts = auth.split(maxsplit=1)
        return len(parts) == 2 and parts[0].lower() == "hash"

    def authenticate(self, request: Request) -> dict:
        auth = request.headers.get("Authorization", "")
        token = auth.split(maxsplit=1)[1]

        token_parts = token.split(":")
        if len(token_parts) != 3:
            raise Unauthorized("Invalid hash format")

        api_key_str, timestamp_str, signature = token_parts

        try:
            timestamp = int(timestamp_str)
        except (TypeError, ValueError):
            raise Unauthorized("Invalid hash format")

        secret = self._get_secret()
        expected_signature = hmac.new(
            secret.encode(),
            timestamp_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise Unauthorized("Invalid hash signature")

        validity_ms = self.validity_seconds * 1000
        current_ms = int(time.time() * 1000)
        elapsed = current_ms - timestamp

        if elapsed > validity_ms or elapsed < 0:
            raise Unauthorized("Hash expired or invalid")

        if self._resolve is None:
            raise RuntimeError(
                "HashBackend: no resolve configured. Pass resolve=... "
                "when registering the backend."
            )

        identity = self._resolve(api_key_str)
        if not identity:
            raise Unauthorized("Invalid or unresolved api key")

        return identity
