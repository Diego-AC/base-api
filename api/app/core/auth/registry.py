from typing import Callable, Dict, List

from .contract import AuthBackend


class RegistryError(Exception):
    """Levantada cuando un backend solicitado no está registrado."""


_BackendFactory = Callable[[], AuthBackend]

_backends: Dict[str, _BackendFactory] = {}


def register_backend(name: str, factory: _BackendFactory) -> None:
    """Registra un backend de autenticación por nombre.

    El fork llama a esta función una vez por backend en su módulo
    central (típicamente ``app/auth.py``). El ``name`` es el string
    que después se pasa al decorador ``@auth_required(['name'])``.

    El ``factory`` es un callable sin argumentos que devuelve una
    instancia fresca de ``AuthBackend``. Se llama una vez por request
    (no al registrar), para permitir backends que lean config de
    runtime.
    """
    if not isinstance(name, str) or not name:
        raise ValueError("Backend name must be a non-empty string")
    if not callable(factory):
        raise ValueError("Backend factory must be callable")
    if name in _backends:
        raise ValueError(f"Backend {name!r} is already registered")
    _backends[name] = factory


def get_backend(name: str) -> AuthBackend:
    """Devuelve una instancia del backend registrado bajo ``name``."""
    if name not in _backends:
        available = sorted(_backends.keys())
        raise RegistryError(
            f"Auth backend {name!r} is not registered. "
            f"Available backends: {available}. "
            f"Did you forget to call register_backend({name!r}, ...) in your "
            f"app/auth.py, or to import app.auth before register_routes?"
        )
    return _backends[name]()


def registered_names() -> List[str]:
    """Devuelve la lista de nombres registrados (ordenada)."""
    return sorted(_backends.keys())


def clear_registry() -> None:
    """Vacía el registry. Útil para tests que necesitan empezar limpios."""
    _backends.clear()
