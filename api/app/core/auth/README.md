# `app/core/auth/`

Mecanismo de autenticación del template. Define un contrato
(`AuthBackend`), un registry y un decorador factory (`auth_required`).
La base provee dos implementaciones listas: `JwtBackend` y
`HashBackend`. El fork registra las suyas (incluidas esas dos, si las
quiere usar) en `app/auth.py` y las invoca por nombre en cada
recurso.

## Diseño en una imagen

```
recurso:
  @auth_required(['jwt', 'hash'])
  def get(self): ...

                │
                ▼
        factory + Marshmallow
                │
                ▼
    registry (registrado en app/auth.py)
        ├── 'jwt'  → JwtBackend
        ├── 'hash' → HashBackend
        └── 'x'    → XBackend (del fork)
                │
                ▼
    can_handle(request) → ¿sabe leer la credencial?
                │
                ▼
    authenticate(request) → valida, devuelve identity dict en g.identity
```

## Endpoints públicos vs protegidos

| Código | Significado |
|---|---|
| `def get(self): ...` | Endpoint público. No requiere auth. |
| `@auth_required(['jwt'])` | Protegido. La app no levanta si `'jwt'` no está registrado. |
| `@auth_required([])` | **Error de programación.** `ValueError` al decorar. |

## Backends disponibles en la base

| Backend | Header | Qué valida | Cuándo usarlo |
|---|---|---|---|
| `JwtBackend` | `Authorization: Bearer <token>` | Firma + `exp` (si presente) + `nbf` (PyJWT default). | Login tradicional, tokens firmados por el servicio o un IdP. |
| `HashBackend` | `Authorization: Hash <api_key>:<ts>:<sig>` | HMAC con `FRONTEND_SECRET` + ventana de tiempo. | Defensa contra bots sobre endpoints públicos (prueba lógica). |

Si necesitás algo más (Google id_token, Redis lookup, IP whitelist,
header firmado por un proxy), implementá un `AuthBackend` en tu fork.

## Cómo estructura tu fork

1. Centralizá tus backends en `app/auth.py`:

    ```python
    from app.core.auth import register_backend
    from app.core.auth.backends import HashBackend, JwtBackend

    register_backend('jwt', lambda: JwtBackend(secret=...))
    register_backend('hash', lambda: HashBackend(secret=..., resolve=...))
    ```

2. Importá ese módulo en `create_app()` **antes** de `register_routes(api)`.
   `app/setup.py` lo hace por vos si lo dejás en `app/auth.py`.

3. En los recursos, usá el decorador con strings:

    ```python
    from app.core.auth import auth_required

    class MyResource(BaseResource):
        @auth_required(['jwt', 'hash'])
        def get(self): ...
    ```

## Mensajes de error frecuentes

| Situación | Mensaje |
|---|---|
| `@auth_required([])` | `@auth_required expects at least one backend. To declare a public endpoint, omit the decorator entirely.` |
| `@auth_required(['redis'])` sin registrar | `Auth backend 'redis' is not registered. Available backends: [...]. Did you forget to call register_backend('redis', ...) in your app/auth.py, or to import app.auth before register_routes?` |
| Cliente sin credencial | `401 Unauthorized: Missing or invalid credentials` |
| Cliente con credencial inválida | `401 Unauthorized: <motivo específico del backend>` |

## Detalle: `JwtBackend` y payloads vacíos

El `JwtBackend` **NO interpreta el payload**. Esto significa que un
token con `payload = {}` o `payload = {"exp": <ts>}` es perfectamente
válido y se acepta igual. El fork decide qué claims emite.

Ejemplo de emisor mínimo:

```python
import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app

def emit_minimal_token(user_id):
    payload = {
        'sub': str(user_id),
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
    )
```

Si necesitás validar `aud` o `iss`, pasalos al instanciar:

```python
register_backend(
    'jwt',
    lambda: JwtBackend(
        secret=os.environ['SECRET_KEY'],
        audience='my-service',
        issuer='auth.example.com',
    ),
)
```

## Detalle: `HashBackend` y `resolve`

El `HashBackend` solo sabe validar la firma y la ventana de tiempo.
La parte "qué hay detrás de un api_key" la provee el fork vía
`resolve`:

```python
def my_resolver(api_key_str):
    # DB, Redis, config, lo que sea.
    row = ApiKey.query.filter_by(api_key=api_key_str, is_active=True).first()
    return {'user_id': row.user_id, 'scopes': row.scopes} if row else None

register_backend(
    'hash',
    lambda: HashBackend(
        secret=os.environ['FRONTEND_SECRET'],
        resolve=my_resolver,
        validity_seconds=15,
    ),
)
```

Si `resolve` devuelve `None` o no se configuró, el backend rechaza
con `401`. **No** loguea, **no** adivina, **no** tiene un modo "fail
open".

## Tests

El template no incluye tests de auth (consistente con el resto de
la base: no tiene tests). El fork testea sus backends, su
`resolve`, y la combinación de modos (`any` / `all`).

Para tests, el helper `clear_registry()` permite empezar limpio:

```python
from app.core.auth import clear_registry, register_backend

def setUp(self):
    clear_registry()
    register_backend('test', lambda: MyTestBackend())
```
