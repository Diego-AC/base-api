"""Registro de backends de autenticación del template.

Este módulo existe como ejemplo. El fork puede:
- Borrarlo y registrar los suyos en su propio ``app/auth.py``.
- Sobreescribirlo con su propia configuración.
- Agregar más backends siguiendo el mismo patrón.

Los backends que la base provee listos son ``JwtBackend`` y
``HashBackend`` (en ``app.core.auth.backends``). El fork implementa
los suyos siguiendo el ``AuthBackend`` Protocol si los necesita.
"""

import os

from flask import current_app

from app.core.auth import register_backend
from app.core.auth.backends import HashBackend, JwtBackend


def _hash_resolver(api_key_str: str):
    """Resolver de ejemplo para ``HashBackend``.

    En el fork, reemplazá esto por la lógica que resuelva
    ``api_key_str -> identity_dict`` desde donde corresponda
    (DB, Redis, config, etc.).

    Este placeholder devuelve ``None`` siempre, lo que hace que
    ``HashBackend`` rechace cualquier credencial. El fork lo nota
    al primer request y reemplaza la función.
    """
    return None


def register_template_backends() -> None:
    register_backend(
        "jwt",
        lambda: JwtBackend(secret=lambda: current_app.config.get("SECRET_KEY", "")),
    )
    register_backend(
        "hash",
        lambda: HashBackend(
            secret=lambda: os.environ.get("FRONTEND_SECRET", ""),
            resolve=_hash_resolver,
            validity_seconds=int(os.environ.get("HASH_VALIDITY_SECONDS", "10")),
        ),
    )


register_template_backends()
