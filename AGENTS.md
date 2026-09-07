# AGENTS.md

Operating manual for AI agents (and humans) working on this codebase.

> If you are an AI: read this file fully, then load the relevant skills from
> `.agents/skills/` before proposing or writing code.

## 1. Stack

- **Language**: Python 3.12.
- **Framework**: Flask 2.2 + Flask-RESTful + Flask-SQLAlchemy 3 + Flask-Migrate
  (Alembic) + Flask-Marshmallow.
- **DB**: PostgreSQL (currently pinned to 12 in `db/Dockerfile`; see TD-08).
- **Runtime**: Docker Compose.

Do **not** propose alternatives (FastAPI, Django, Pydantic, SQLModel, etc.)
without a strong justification and an explicit OK from the user.

## 2. Pattern

This template uses the **Resource-Repository** pattern with four application
layers and a `core` package. See [README.md §3](README.md#3-architecture) for
the architecture diagram and layer responsibilities.

## 3. Repo map

```
base-api/
├── api/
│   ├── app/
│   │   ├── core/           # cross-cutting (response, errors, logger, auth)
│   │   ├── models/         # SQLAlchemy models (+ base mixins)
│   │   ├── schemas/        # Marshmallow schemas (+ base)
│   │   ├── repositories/   # DB access (+ base mixins)
│   │   ├── resources/      # Flask-RESTful resources (+ base)
│   │   ├── routes.py       # route registration
│   │   ├── config.py       # config classes
│   │   ├── extensions.py   # db, migrate, ma singletons
│   │   └── setup.py        # Flask app factory
│   ├── migrations/         # Alembic
│   ├── app.py              # entrypoint
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── db/
│   ├── Dockerfile
│   └── create.sql
├── docker-compose.yaml
├── .agents/skills/         # AI skills (see SKILL_INDEX.md)
├── .ai-resources/local/    # local-only resources (TECH_DEBT.md lives here)
└── README.md
```

## 4. How to read the project (first time)

Read the files in this order to build a correct mental model:

1. `api/app/setup.py` — how the app is wired.
2. `api/app/extensions.py` — what shared singletons exist.
3. `api/app/config.py` — config classes.
4. `api/app/routes.py` — public surface (URLs).
5. One full module: `models/versions.py` → `schemas/versions.py` →
   `repositories/versions.py` → `resources/versions.py`.
6. `api/app/core/errorhandlers.py` and `core/responses.py` — the response
   contract.

## 5. Hard rules

Violations require explicit user approval.

- **R1** — Use `APIResponse` for every HTTP response. Never `jsonify`, never
  raw dicts.
- **R2** — Inside resources, raise `werkzeug.HTTPException` for error cases.
  Do not return `APIResponse.error(...)` directly.
- **R3** — Only the `repositories/` layer touches `db.session` /
  `Model.query`. Resources do not query the DB.
- **R4** — Schemas are split: `BaseAutoSchema` for output, plain `Schema`
  for input. Never both.
- **R5** — Use `schema.load(payload)` and **capture the result** before
  passing it to the repository (TD-06).
- **R6** — Don't fix `error_handler_resources` (TD-01) on the side of an
  unrelated task. Plan it, then do it.
- **R7** — Don't add dependencies without justification. Update
  `requirements.txt` and explain why.
- **R8** — Don't change `Dockerfile` defaults that affect production safety
  (`FLASK_DEBUG`, exposed ports) without explicit confirmation.
- **R9** — Don't commit `.env`, credentials, generated caches or migration
  files that weren't reviewed.
- **R10** — Don't propose replacing Flask-RESTful, SQLAlchemy or
  Marshmallow. The stack is fixed by template.

## 6. How to create a new module

Use the recipe: [`.agents/skills/create-module/SKILL.md`](.agents/skills/create-module/SKILL.md).

Quick summary: model → schemas → repository → resource → route → migration →
smoke test.

## 7. Conventions

All code-level conventions (naming, response shape, error handling, soft
delete, imports, migrations, status codes, things to avoid) live inline in
this file under §5 above. When in doubt, re-read R1–R10 before asking.

## 8. Canonical commands

```bash
# boot the stack
docker compose up --build

# wait for DB, then run migrations (inside the api container)
docker compose exec api flask db upgrade

# create a new migration after changing models
docker compose exec api flask db migrate -m "add foos"

# open a shell in the api container
docker compose exec api sh
```

## 9. Living tech debt

`.ai-resources/local/TECH_DEBT.md` lists known issues with severity and
locations. Read it before refactoring, and reference the relevant `TD-XX`
when you propose a fix.

Hard rule: do **not** silently fix tech debt as a side-effect of another
task. Surface it, propose the fix, get approval, then do it. Update the
`TECH_DEBT.md` entry (move it to `Resolved`).

## 10. AI workflow

When asked to add or change code:

1. Identify which layer(s) the change touches.
2. Check the matching skill (`create-module`, `commit-message`,
   `update-schema`).
3. Check `TECH_DEBT.md` for items in the same area — flag them.
4. Propose a diff that respects the hard rules (R1–R10).
5. If the diff needs to touch a debt item, propose two PRs or call it out
   explicitly.
6. If a model, relation, or migration changed, update [`SCHEMA.md`](SCHEMA.md)
   in the **same commit**. Use the [`update-schema`](.agents/skills/update-schema/SKILL.md)
   skill.

When asked to write or shape a commit message, load
[`commit-message`](.agents/skills/commit-message/SKILL.md). It defines the
title format, the type vocabulary, and when a body is warranted.

When asked to explain the project, follow section 4 (read order).

When asked to refactor, identify the smallest change that aligns with the
existing pattern; do not invent a new pattern.
