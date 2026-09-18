# Technical Debt Register

Living register of issues, smells and missing pieces in `base-api`.
New items must be added at the bottom of their severity block.

## Format

```
- **TD-XX — short title**
  · file:line(s)
  · impact
  · suggested fix
```

## Status legend

- `pending` — known, not started
- `in-progress` — being worked on
- `done` — resolved (move to a "Resolved" section at the bottom, do not delete)

---

## Critical

- **TD-01 — `error_handler_resources` does not catch `HTTPException` inside resources**
  · `api/app/core/errorhandlers.py:10-27`, `api/app/setup.py:9-12`
  · `HTTPException` raised inside `get/post/...` (e.g. `NotFound` in `LastVersionResource.get`) escapes the wrapper because `CustomApi.handle_error` only does `raise err`; the inner `try/except` is never reached. Only exceptions raised *outside* a resource method are normalised.
  · Apply the wrapper to `BaseResource.dispatch` (or per HTTP method) instead of `handle_error`. Add a regression test that raises `NotFound` from a resource and asserts `APIResponse.error` shape.

- **TD-02 — Database name `principal` is problematic in Postgres**
  · Moved to Resolved.

- **TD-03 — `FLASK_DEBUG=1` hardcoded in Dockerfile**
  · Moved to Resolved. No follow-up on the production side; optional defence-in-depth assertion belongs in a new TD if/when desired.

## High

- **TD-04 — `login_required` does not validate the token**
  · `api/app/core/authentication.py:6-23`
  · Only checks header presence. If used as-is, every authenticated endpoint is effectively public.
  · **Decision**: keep as an intentional placeholder. Auth strategy varies per project (Google OAuth, custom user store, mocked). Document this in `AGENTS.md` and the `conventions` skill. Provide a `AuthBackend` Protocol so real implementations can plug in.

- **TD-05 — `fields.Int(nullable=False, ...)` is a no-op in Marshmallow**
  · `api/app/schemas/versions.py:17`
  · `nullable` is not a Marshmallow kwarg. The keyword for "accept null" is `allow_none`. This silently does nothing and misleads readers.
  · Remove `nullable=False` or replace with `allow_none=True`.

- **TD-06 — `schema.load(payload)` result is discarded**
  · `api/app/resources/versions.py:30-32`
  · Validation runs but the validated object is thrown away; the repo receives the raw dict. Loses schema-driven coercion and breaks `load_instance=True` later.
  · Assign `payload = schema.load(payload)` and pass the validated object (or a dict derived from it) to the repo.
  · **Note (architectural decision)**: do **not** "fix" by saving `schema.load()` result and forwarding it. In Flask-Marshmallow, `load_instance=True` returns a model instance, which would move object construction from the repository to the schema — breaking the Resource-Repository pattern (R3: only repositories touch the model). Preferred direction is to use `schema.validate(payload)` (raises `ValidationError` on failure) and keep the raw dict flowing into the repo. Re-evaluate if/when TD-15 lands and we add real validation tests.

- **TD-07 — `BaseRepository` mixes `ABC` with a commented `@abstractmethod`**
  · `api/app/repositories/base/mixins.py:1, 20, 28`
  · `ABC` is inherited but neither `get_or_create` nor `create` is enforced. The pattern pretends to be a contract that it isn't.
  · Either remove `ABC` and treat the class as a concrete helper, or properly `@abstractmethod` the methods (and fix the signature mismatch with `VersionRepository.create(self, dataJson)` vs `create(self, **kwargs)`).

- **TD-08 — Postgres 12 is EOL**
  · Moved to Resolved.

- **TD-09 — Migrations are not applied on container start**
  · Moved to Resolved for production. The dev-entrypoint gap stays open as a new item below (TD-09b — see "TD-09b" entry).

- **TD-10 — `psycopg2-binary` in requirements**
  · `api/requirements.txt:19`
  · Fine for dev. Not recommended for production builds (binary wheel, no system-lib isolation).
  · Document in README; optionally split `requirements-dev.txt` / `requirements-prod.txt`.
  · **Note**: now that `Dockerfile.production` exists, the cleanest move is to switch prod to `psycopg2` (source build, system libs) and keep `psycopg2-binary` only for dev. The README update would document the split.

## Medium

- **TD-11 — README is a folder tree**
  · Moved to Resolved.

- **TD-12 — No `.env.example`**
  · repo root
  · No reference of required env vars for a new dev.
  · Create `.env.example` with `FLASK_DEBUG`, `WAIT_DB`, `POSTGRES_*`, etc.

- **TD-13 — `.env*` lines are commented out in `.gitignore`**
  · `.gitignore:39-44`
  · Trivially bypassed: someone `git add .env` and it goes in.
  · Uncomment. Add `!.env.example` so the example is still tracked.
  · **Observed during prod setup**: creating `api/.env` for the prod smoke test left it as an untracked file that `git status` happily surfaces. Any teammate running `git add .` would commit it. Fix should be uncommented together with TD-12 so the template `.env.example` survives.

- **TD-14 — No linter/formatter config**
  · repo
  · No enforced style; AI-generated code drifts.
  · Add `ruff` (lint + format) + `pyproject.toml` config; optional `pre-commit`.

- **TD-15 — No tests**
  · repo
  · No safety net for refactors or TD-01-style bugs.
  · Add `tests/` with `pytest`; cover the error handler (TD-01) as first case.

- **TD-16 — No healthcheck or restart policy in compose**
  · Moved to Resolved for production. Dev-compose gap stays open as TD-16b below.

- **TD-17 — CORS not configured**
  · `api/app/setup.py`
  · Frontends on other origins cannot call the API.
  · Add `Flask-CORS` with a configurable allow-list (no `*` in prod).

- **TD-18 — No rate limiting**
  · `api/app/setup.py`
  · Exposed API without brute-force / abuse protection.
  · Add `Flask-Limiter` with per-IP defaults; configurable per-endpoint.

- **TD-19 — `active` is `SmallInteger` without an index**
  · `api/app/models/versions.py:11`
  · Soft-delete filters do full table scans once data grows.
  · Migrate to `db.Boolean` (cleaner semantics) and `index=True`.

- **TD-20 — `_force_delete` is dead code**
  · `api/app/models/base/mixins.py:14-16`
  · Never referenced. Confuses readers ("when do I use this?").
  · Document in a comment or remove until needed.

- **TD-09b — Dev entrypoint does not run migrations (gap from TD-09)**
  · Moved to Resolved.

- **TD-16b — Dev compose has no healthcheck or restart policy (gap from TD-16)**
  · Moved to Resolved.

## Low

- **TD-21 — `get_or_fail` uses deprecated Flask-SQLAlchemy 3 API**
  · `api/app/repositories/base/mixins.py:39-40`
  · `Query.get_or_404` triggers a deprecation warning on 3.x.
  · Replace with `db.session.get_or_404(Model, _id)`.

- **TD-22 — `BaseRepository.create` signature inconsistent with subclasses**
  · `api/app/repositories/base/mixins.py:28-34` vs `api/app/repositories/versions.py:12`
  · Base says `**kwargs`, subclass takes `dataJson`. Cosmetic.
  · Pick one (prefer `**kwargs`) and document it.

- **TD-23 — `.agents/skills/` and `.ai-resources/local/` are empty placeholders**
  · Moved to Resolved.

- **TD-24 — Missing `LICENSE`, `.editorconfig`, `CONTRIBUTING.md`**
  · repo root
  · Polish. Affects how external devs onboard.
  · Add per project policy.

- **TD-25 — Logger hardcoded to a fixed name `multi_console_logger`**
  · `api/app/core/logger.py:15`
  · Looks copy-pasted from another project; odd name for a template.
  · Use `__name__` or a configurable project logger name.

- **TD-26 — `getattr(self.model, order_by.key)` has no type guard**
  · `api/app/repositories/base/mixins.py:97`
  · If `order_by.key` is wrong type or missing, silent fallback to `id.asc()`.
  · Raise `ValueError` with a clear message instead.

---

## Resolved

- **TD-01 — `error_handler_resources` does not catch `HTTPException` inside resources**
  · Resolved by extracting `normalize_error(e)` (single source of truth) in `api/app/core/errorhandlers.py`, wrapping `BaseResource.dispatch` (covers every HTTP verb), and registering `app.errorhandler(HTTPException)` + `app.errorhandler(Exception)` so framework-level errors (404 routing, 405) also produce the `APIResponse.error` shape. `CustomApi` removed. Verified manually with `curl` (health, `NotFound` from resource, unknown route, `ValidationError`, 405). Automated test pending (see TD-15).

- **TD-03 — `FLASK_DEBUG=1` hardcoded in Dockerfile**
  · Resolved in `Dockerfile.production` (no `ENV FLASK_DEBUG`) and in the dev `Dockerfile` (the hardcoded `ENV` was removed). `api/entrypoint.sh` now reads `FLASK_DEBUG` at runtime and only adds `--debug` when explicitly set. The RCE risk from a leaked prod container is gone.

- **TD-09 — Migrations are not applied on container start**
  · Resolved in production: `api/entrypoint.prod.sh` runs `flask db upgrade` before exec'ing gunicorn. The dev-side gap is tracked separately as TD-09b.

- **TD-11 — README is a folder tree**
  · Resolved: README now covers the stack, the architecture diagram, the Resource-Repository layers, the quickstart, env vars, AI workspace rules, the new-module recipe, the production deployment section (image, entrypoint contract, compose, required `backend-network`), and pointers to `AGENTS.md` / `SCHEMA.md` / `TECH_DEBT.md`.

- **TD-16 — No healthcheck or restart policy in compose**
  · Resolved in production: `docker-compose.prod.yaml` has `healthcheck` (curl `/`) and `restart: always`. The dev-compose gap is tracked separately as TD-16b.

- **TD-23 — `.agents/skills/` and `.ai-resources/local/` are empty placeholders**
  · Resolved: `.agents/skills/` now has `commit-message`, `create-module`, `update-schema`, and a `SKILL_INDEX.md`. `.ai-resources/` is split into `issues/` (tracked, shared tech debt register) and `local/` (git-ignored scratchpad with a `.gitkeep`). The README §6 documents the contract for `local/`. The tech debt register lives in `issues/`, not `local/` (cleaner split than the original TD-23 implied).

- **TD-09b — Dev entrypoint does not run migrations (gap from TD-09)**
  · Resolved: `api/entrypoint.sh` now runs `flask db upgrade` when `RUN_MIGRATIONS=1`, and `docker-compose.yml` sets that flag by default. A fresh `docker compose up --build` applies migrations on boot.

- **TD-16b — Dev compose has no healthcheck or restart policy (gap from TD-16)**
  · Resolved: `docker-compose.yml` now mirrors the prod contract. Postgres has a `pg_isready` healthcheck; the api has a `wget --spider` healthcheck on `/` and `restart: unless-stopped`. The api waits on `postgres: condition: service_healthy` before booting. Verified end-to-end by killing PID 1 inside the api container: Docker brought it back up `healthy` in under 15 seconds.

- **TD-02 — Database name `principal` is problematic in Postgres**
  · Resolved: the database is now created through the official Postgres image `POSTGRES_DB` env var (default `sample`), making it overridable from `.env` without touching code. The local `db/Dockerfile` and `db/create.sql` were removed in favour of the image's built-in init. `DevConfig.SQLALCHEMY_DATABASE_URI` and `.env.example` use the same env var. The chosen default `sample` is intentionally honest about being a placeholder: anyone who sees it in a `psql -l` listing in production can tell at a glance that it was never renamed. Each downstream project should set `POSTGRES_DB` to its service name (e.g. `scheduler` for `api-scheduler`).

- **TD-08 — Postgres 12 is EOL**
  · Resolved: bumped from `postgres:12.4-alpine` (frozen since the November 2024 EOL) to `postgres:16-alpine` in `docker-compose.yml`. Hard reset with `docker compose down --rmi all -v && docker compose build --no-cache`, then a full smoke test confirmed Postgres 16.14 is running, the `sample` DB is created by `POSTGRES_DB`, Alembic migrations apply cleanly to the same head, both services reach `healthy` on first boot, and a round-trip insert via psql + read via `GET /versions/last` returns the expected payload.
