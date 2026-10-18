from typing import Protocol, runtime_checkable

from flask import Request


@runtime_checkable
class AuthBackend(Protocol):
    """Contrato que todo mecanismo de autenticación debe cumplir.

    La base provee dos implementaciones listas (``JwtBackend`` y
    ``HashBackend``, en ``app.core.auth.backends``). Cada fork puede
    agregar las suyas siguiendo este mismo contrato.

    Un backend decide si sabe interpretar la credencial del request
    (``can_handle``) y, si la sabe, la valida y devuelve un dict con
    la identidad (``authenticate``). Si la credencial es inválida,
    levanta ``werkzeug.exceptions.Unauthorized``.

    El dict de identidad que devuelve ``authenticate`` queda expuesto
    en ``flask.g.identity`` y es opaco: el backend no interpreta sus
    campos, el fork lo lee como quiera.
    """

    name: str

    def can_handle(self, request: Request) -> bool: ...

    def authenticate(self, request: Request) -> dict: ...
