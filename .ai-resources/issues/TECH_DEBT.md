# Technical Debt Register

Registro vivo de problemas, malos olores y piezas faltantes en `base-api`.
Los items nuevos se agregan al final del bloque de su severidad.

## Formato

```
- **TD-XX — título corto**
  · archivo:línea(s)
  · impacto
  · fix sugerido
```

## Leyenda de estado

- `pending` — conocido, no empezado
- `in-progress` — en curso
- `done` — resuelto (mover a la sección "Resolved" al final, no borrar)

---

## Critical (Crítico)

(none at the moment)

## High (Alto)

(none at the moment)

## Medium (Medio)

(vacío)

---

## Low (Bajo)

- **TD-20 — `_force_delete` parece código muerto en este proyecto, pero es parte del template**
  · `api/app/models/base/mixins.py:14-16`
  · **En criollo**: este proyecto base no lo usa nunca. El `delete()` normal hace soft-delete (`active = 0`); el `_force_delete` hace un `DELETE` físico. Cualquier IA que mire la base va a decir "esto está muerto, bórralo". **No es deuda, es diseño del template**.
  · **Por qué se queda**: este repo es una base reutilizable. Hay casos reales donde se necesita borrado físico: GDPR/derecho al olvido, purga de blobs en storage, cumplimiento regulatorio, jobs de limpieza, sistemas que sincronizan con otra fuente de verdad. Quien clone la base para uno de esos casos necesita que el mecanismo ya esté. Borrarlo es mutilar la plantilla.
  · **Acción**: ninguno. Si te lo cruzás revisando, NO lo borres. Si en un proyecto final no lo usás, lo borrás *en ese fork*, no acá.


## Low (Bajo)

(vacío)

---

## Future work (Trabajo futuro)

- **TD-27 — Protocolo `AuthBackend` para autenticación que no sea JWT**
  · `api/app/core/authentication.py`
  · **En criollo**: hoy el decorador `@login_required` está pegado con cinta a JWT HS256. Si mañana querés soportar OAuth, API Keys, sesiones, o mocks para tests, tenés que duplicar el decorador. Esto no es un problema hoy (JWT funciona), pero la idea es dejar escrita la dirección de cómo se va a resolver cuando llegue el momento.
  · **Dirección propuesta (no implementar hasta que decidas rediseñar auth)**: definir un `typing.Protocol` (`AuthBackend.authenticate(request) -> dict | raise`). El decorador `login_required` aceptaría un `backend: AuthBackend` como parámetro (default a `JwtBackend`). Habría implementaciones concretas: `JwtBackend` (la actual) y `NoAuthBackend` (para endpoints públicos o tests).
  · **Por qué está acá y no en el backlog**: JWT funciona, nada en el código actual lo necesita todavía. Esto está para que la decisión de diseño no se pierda, no como tarea pendiente.

---

## Resolved (Resueltos) — resumen express

- **TD-01** — Los errores HTTP dentro de los recursos se escapaban. Resuelto: `normalize_error` + wrapper en `BaseResource.dispatch` + handlers globales.
- **TD-02** — El nombre de DB "principal" daba problemas en Postgres. Resuelto: ahora se llama "sample" y se puede cambiar vía env var.
- **TD-03** — `FLASK_DEBUG=1` hardcodeado en Dockerfile era riesgo RCE en prod. Resuelto: se lee de env al arranque.
- **TD-04** — `login_required` no validaba el token (decorador decorativo). Resuelto: ahora decodifica JWT con PyJWT y `SECRET_KEY`.
- **TD-05** — `fields.Int(nullable=False, ...)` era un kwarg falso. Resuelto: borrado, ahora es `fields.Int()`.
- **TD-06** — `schema.load(payload)` se descartaba. Resuelto: ahora `payload = schema.load(payload)` y se pasa el resultado al repo. **El fix NO fue `schema.validate(payload)` como sugería la nota original** — al implementarlo descubrimos que `validate()` no respeta `required=True` (devuelve OK con `{}`), por lo que payloads inválidos seguían llegando al repo e insertando basura en la DB. La solución correcta es capturar el resultado de `load()`, que sí valida `required` y tipos. Como `PayloadVersionSchema` es un `Schema` plano (no hereda de `BaseAutoSchema`), `load_instance` no está activo, así que `load()` devuelve un dict validado y R3 se sigue respetando (el modelo lo construye el repo, no el schema). Bug colateral destapado: el POST con `{}` antes insertaba un registro con `description=null` y reventaba con `NotNullViolation` 500; ahora corta en 400 con el detalle del campo faltante.
- **TD-19** — `active` era `SMALLINT` sin índice. Resuelto: ahora es `db.Boolean` con `index=True` y default `True` a nivel Python (un nuevo registro nace activo, no inactivo — es la semántica esperada). Migración `f3ea58733afb` convierte la columna existente usando `(active <> 0)` (Postgres necesita coerción explícita `SMALLINT → BOOLEAN`) y crea el índice `ix_versions_active`. `VersionRepository.create` actualizado para usar `True` como fallback. `SCHEMA.md` actualizado en el mismo cambio.
- **TD-07** — `BaseRepository` mezclaba `ABC` con `@abstractmethod` y no cumplía el contrato que prometía. Resuelto: `ABC` y los `@abstractmethod`/`pass` stubs fuera; la base ahora es helper concreto, expone defaults para `create(**kwargs)` y `get_or_create(defaults=None, **kwargs)` que sirven para el caso simple, y documenta en `AGENTS.md` (R14) que la firma concreta de `create`/`get_or_create` la define cada repo hijo. `VersionRepository.create(self, dataJson)` queda intacto porque su firma es la que su dominio necesita.
- **TD-21** — `get_or_fail` usaba `self.query.get_or_404` (API vieja de Flask-SQLAlchemy 2, deprecated en 3). Resuelto: ahora arma el query en el repositorio y usa `first_or_404()` sobre él: `self.query.filter_by(id=_id).first_or_404()`. Esto respeta R3 (el query se construye en el repo, no se delega al shortcut `db.get_or_404(...)` que vive fuera del repositorio y rompe el patrón Resource-Repository).
- **TD-22** — Las firmas de `create` entre base e hijos no coincidían. NO se unificaron: esa es justamente la decisión correcta en una base reutilizable. Resuelto mediante TD-07: la base deja de pretender fijar la firma, y AGENTS.md R14 deja escrito que la firma la define el repo concreto. `VersionRepository.create(self, dataJson)` mantiene su firma porque es lo que su dominio pide.
- **TD-25** — Logger hardcodeado al nombre `multi_console_logger`. Resuelto: el nombre ahora viene de `BaseConfig.LOGGER_NAME` (default `"app"`) y `setup.py` re-registra el logger con ese nombre después de cargar la config (`_bind_logger_name`). **No se lee de env** por decisión explícita: cada fork sobreescribe subclaseando `BaseConfig` e inyectando via `create_app(config=...)`. Documentado en `README.md` §5 "Config overrides (not env)". Bug colateral del handler de ERROR arreglado de paso: el formatter reventaba con `KeyError('file_path')` cuando un `logger.error(...)` se llamaba sin `extra={'file_path': ..., 'line_number': ...}`; ahora un `Filter` rellena los campos faltantes desde `record.pathname` / `record.lineno` para que cualquier call site no rompa.
- **TD-08** — Postgres 12 estaba EOL desde noviembre 2024. Resuelto: bumpeado a 16-alpine.
- **TD-09** — Las migraciones no se aplicaban al arrancar el contenedor en prod. Resuelto: `entrypoint.prod.sh` corre `flask db upgrade` antes de gunicorn.
- **TD-09b** — El entrypoint de dev tampoco corría migraciones. Resuelto: `docker-compose.yml` setea `RUN_MIGRATIONS=1`.
- **TD-11** — El README era un árbol de carpetas. Resuelto: ahora documenta stack, arquitectura, quickstart, env vars, deploy de prod.
- **TD-12** — No había `.env.example`. Resuelto: existe en la raíz con todas las variables documentadas.
- **TD-13** — Las líneas de `.env*` estaban comentadas en `.gitignore`. Resuelto: ahora se ignoran `.env` y `.env.*`, excepto `.env.example`.
- **TD-16** — Faltaban healthcheck y restart policy en compose de prod. Resuelto: `docker-compose.prod.yaml` los tiene.
- **TD-16b** — Faltaban también en dev. Resuelto: dev compose ahora espeja el contrato de prod.
- **TD-17** — CORS no estaba configurado. Resuelto: `flask-cors` instalado, `CORS_ALLOWED_ORIGINS` en config, default a `[]` en prod.
- **TD-18** — No había rate limiting. Resuelto: `Flask-Limiter` instalado, **opt-in** (off por default, no rompemos proyectos downstream).
