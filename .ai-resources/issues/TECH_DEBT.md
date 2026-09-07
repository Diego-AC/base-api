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
  · `db/create.sql:1`, `api/app/config.py:16`, `docker-compose.yaml`
  · `principal` is a confusing identifier and overlaps with reserved/role-like words in some Postgres contexts; quoting it across tools and migrations is a footgun.
  · Rename to a neutral name (`appdb`, `app`, etc.). Update `create.sql`, `DevConfig.SQLALCHEMY_DATABASE_URI`, compose env, README and migration history.
  · **Status**: pending. Out of scope for the docs/AI iteration.

- **TD-03 — `FLASK_DEBUG=1` hardcoded in Dockerfile**
  · `api/Dockerfile:5`
  · Exposes the Werkzeug interactive debugger if the container ever runs without an override. A leaked prod container becomes RCE-as-the-app-user.
  · Read `FLASK_DEBUG` from env with no default, or default to `0`. Document that the prod compose overrides it. Add a CI check or startup assertion that refuses to boot if `FLASK_DEBUG=1` in a non-dev profile.

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

- **TD-07 — `BaseRepository` mixes `ABC` with a commented `@abstractmethod`**
  · `api/app/repositories/base/mixins.py:1, 20, 28`
  · `ABC` is inherited but neither `get_or_create` nor `create` is enforced. The pattern pretends to be a contract that it isn't.
  · Either remove `ABC` and treat the class as a concrete helper, or properly `@abstractmethod` the methods (and fix the signature mismatch with `VersionRepository.create(self, dataJson)` vs `create(self, **kwargs)`).

- **TD-08 — Postgres 12 is EOL**
  · `db/Dockerfile:1`
  · Postgres 12 reached end-of-life in November 2024. No security patches.
  · Bump to `postgres:16-alpine` (or current LTS). Re-test migrations.

- **TD-09 — Migrations are not applied on container start**
  · `api/entrypoint.sh`
  · First-time setup requires `docker compose exec api flask db upgrade`. Easy to forget on a fresh clone.
  · Add an opt-in `RUN_MIGRATIONS=1` step in `entrypoint.sh` that runs `flask db upgrade` before `flask run`. Document the env var.

- **TD-10 — `psycopg2-binary` in requirements**
  · `api/requirements.txt:19`
  · Fine for dev. Not recommended for production builds (binary wheel, no system-lib isolation).
  · Document in README; optionally split `requirements-dev.txt` / `requirements-prod.txt`.

## Medium

- **TD-11 — README is a folder tree**
  · `README.md`
  · A new dev cannot tell the stack, the pattern or how to boot the project from the README alone.
  · Rewritten in this iteration.

- **TD-12 — No `.env.example`**
  · repo root
  · No reference of required env vars for a new dev.
  · Create `.env.example` with `FLASK_DEBUG`, `WAIT_DB`, `POSTGRES_*`, etc.

- **TD-13 — `.env*` lines are commented out in `.gitignore`**
  · `.gitignore:39-44`
  · Trivially bypassed: someone `git add .env` and it goes in.
  · Uncomment. Add `!.env.example` so the example is still tracked.

- **TD-14 — No linter/formatter config**
  · repo
  · No enforced style; AI-generated code drifts.
  · Add `ruff` (lint + format) + `pyproject.toml` config; optional `pre-commit`.

- **TD-15 — No tests**
  · repo
  · No safety net for refactors or TD-01-style bugs.
  · Add `tests/` with `pytest`; cover the error handler (TD-01) as first case.

- **TD-16 — No healthcheck or restart policy in compose**
  · `docker-compose.yaml`
  · Containers can stay zombie on crash.
  · Add `healthcheck` to `postgres` and `api`, `restart: unless-stopped` for dev convenience.

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
  · dirs
  · Promised in the template structure but unused.
  · Populated in this iteration.

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

_(move items here when fixed; keep the original `TD-XX` for traceability)_
