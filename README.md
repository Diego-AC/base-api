# base-api

Opinionated Flask template for REST APIs, built around a thin
**Resource-Repository** pattern. Use it to bootstrap a new service without
re-deciding the architecture every time.

## 1. What it is

`base-api` is a starting point, not a framework. It ships with:

- Docker Compose for the API and PostgreSQL.
- Alembic migrations wired through Flask-Migrate.
- A sample module (`versions`) you can copy as a template for new entities.
- Uniform response shape (`{message, status, data}`) for every endpoint.
- A documented set of conventions and AI skills so future contributors
  (human or otherwise) stay aligned.

The rule of thumb: every new domain entity follows the same recipe —
`model → schema → repository → resource → route → migration`.

## 2. Stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Web framework | Flask 2.2 + Flask-RESTful |
| ORM | Flask-SQLAlchemy 3 (SQLAlchemy 2) |
| Migrations | Flask-Migrate (Alembic) |
| Serialisation | Flask-Marshmallow |
| Database | PostgreSQL (12 in dev compose; see TD-08) |
| Runtime | Docker Compose |

Do not propose alternatives (FastAPI, Django, Pydantic, SQLModel, …) without
strong justification and an explicit OK.

## 3. Architecture

```
HTTP request
   │
   ▼
┌──────────────┐    validate     ┌──────────────┐
│   Resource   │ ──────────────▶ │   Schema     │   (Marshmallow)
│  (HTTP I/O)  │                 └──────────────┘
└──────┬───────┘
       │ call method
       ▼
┌──────────────┐    read/write   ┌──────────────┐
│ Repository   │ ──────────────▶ │    Model     │   (SQLAlchemy)
│ (queries)    │                 └──────┬───────┘
└──────────────┘                        │
                                       ▼
                                ┌──────────────┐
                                │  PostgreSQL  │
                                └──────────────┘
       │
       ▼
┌──────────────┐
│ APIResponse  │   {message, status, data}
└──────────────┘
```

### Layers

- `app/resources/` — HTTP handlers (Flask-RESTful `Resource` subclasses).
  Receives the request, picks a schema, calls a repository, wraps the
  response.
- `app/schemas/` — Marshmallow schemas. `BaseAutoSchema` for output,
  plain `Schema` for input payloads.
- `app/repositories/` — the **only** layer that talks to `db.session` and
  `Model.query`. Exposes CRUD-ish methods plus domain queries.
- `app/models/` — SQLAlchemy entities, mixed with `TransactionalMixin`
  for `save / update / logical delete`.
- `app/core/` — cross-cutting: `APIResponse`, error handlers, logger,
  `login_required` placeholder.

For the step-by-step recipe to add a new module, see
[`.agents/skills/create-module/SKILL.md`](.agents/skills/create-module/SKILL.md).

## 4. Quickstart

Requirements: Docker + Docker Compose.

```bash
# 1. Boot the stack (api + postgres)
docker compose up --build

# 2. In another terminal, apply migrations once the DB is up
docker compose exec api flask db upgrade

# 3. Smoke test the sample module
curl -s -X POST http://localhost:5050/versions \
  -H 'Content-Type: application/json' \
  -d '{"description":"hello world"}'

curl -s http://localhost:5050/versions/last
```

A successful response looks like:

```json
{
  "message": "Ok",
  "status": 1,
  "data": { "id": 1, "description": "hello world" }
}
```

## 5. Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `WAIT_DB` | unset | When `1`, the API entrypoint waits for `postgres:5432` before booting. Set to `1` for the default `docker-compose.yaml`. |
| `FLASK_DEBUG` | `1` in dev `Dockerfile` | Enables Flask reloader + Werkzeug debugger. **Override to `0` in any prod-like compose.** See TD-03. |
| `FLASK_APP` | `app.py` | Flask entrypoint module. |
| `PORT` | `5050` | Port the API listens on. |
| `SQLALCHEMY_DATABASE_URI` | (set in `config.py`) | Postgres connection string. Override per environment. |
| `PYTHONPATH` | `/api` | Set in the image so `flask` finds the app package. |

> No `.env.example` is shipped yet (TD-12). For now, copy the values above
> into a local `.env` and keep it out of version control.

## 6. Per-developer AI workspace

`.ai-resources/local/` is a **scratchpad for your AI assistant**. Use it to
drop context that helps the AI work on this project but should never leave
your machine: debugging notes, scratch queries, prompt drafts, transcripts,
in-progress designs, anything personal to your workflow.

Rules:

- **Git-ignored by default.** Everything inside `local/` is excluded by
  `.gitignore`, so it will never appear in `git status` and cannot be
  committed by accident. The folder itself is preserved via
  `.ai-resources/local/.gitkeep`.
- **Shared content goes elsewhere.** Anything that should ship with the
  repo (canonical tech debt register, shared AI skills, project-wide docs)
  lives one level up in `.ai-resources/` — e.g. `.ai-resources/issues/` —
  and is tracked normally.
- **Safe to delete.** If you want a clean slate, just `rm -rf
  .ai-resources/local/*`. The folder will be recreated on the next clone
  thanks to the `.gitkeep`.
- **No rules on shape.** Naming, format and structure inside `local/` are
  entirely up to you and your AI. Don't bikeshed it.

If you want a small README inside `local/` to remind future-you of how you
use it, that's allowed (the `.gitignore` exception lets it through).

## 7. Add a new module

The shortest path from "I need a `Foo` resource" to a working endpoint:

1. `api/app/models/foo.py` — `Foo(db.Model, TransactionalMixin)`.
2. `api/app/schemas/foo.py` — `FooSerializer(BaseAutoSchema)` +
   `PayloadFooSchema(Schema)`.
3. `api/app/repositories/foo.py` — `FooRepository(BaseRepository)`.
4. `api/app/resources/foo.py` — `FooResource(BaseResource)`.
5. Register the routes in `api/app/routes.py`.
6. Generate + apply the migration:
   ```bash
   docker compose exec api flask db migrate -m "add foos"
   docker compose exec api flask db upgrade
   ```
7. Smoke test with `curl`.

Full step-by-step with snippets:
[`.agents/skills/create-module/SKILL.md`](.agents/skills/create-module/SKILL.md).

---

## More

- AI agent operating manual: [`AGENTS.md`](AGENTS.md).
- Database schema index: [`SCHEMA.md`](SCHEMA.md).
- Known issues and roadmap: [`.ai-resources/local/TECH_DEBT.md`](.ai-resources/local/TECH_DEBT.md).
- All skills at a glance: [`.agents/skills/SKILL_INDEX.md`](.agents/skills/SKILL_INDEX.md).
- Writing a commit message? Use the
  [`commit-message`](.agents/skills/commit-message/SKILL.md) skill for the
  title format and body rules.
- Changed a model or generated a new migration? Use the
  [`update-schema`](.agents/skills/update-schema/SKILL.md) skill to keep
  `SCHEMA.md` in sync in the same commit.
