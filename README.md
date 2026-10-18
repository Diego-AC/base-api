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

### Authentication (`app/core/auth/`)

Authentication is pluggable via an `AuthBackend` Protocol. The
template ships with two concrete backends (`JwtBackend` and
`HashBackend`); the fork registers its own in `app/auth.py` and uses
the `@auth_required(['name1', 'name2'])` decorator on resources.

- The factory is `auth_required(backends: list[str], mode: str = "any")`.
  It is a factory, not a decorator: the resources import the function
  and decorate the method.
- `[]` is an error — public endpoints omit the decorator.
- A name that is not registered raises `RegistryError` at decoration
  time, so the app does not boot. No silent fallback.
- `JwtBackend` validates the signature and the `exp` claim. It does
  **not** interpret the payload — what you put in the JWT is what
  you get in `g.identity`. The fork decides what to emit.
- `HashBackend` validates a `Authorization: Hash <key>:<ts>:<sig>`
  header using `FRONTEND_SECRET` and a time window. The fork injects
  the `resolve(api_key_str) -> identity_dict` function; the backend
  does not know what is behind the api key.

For the full contract, the table of available backends, and the fork
authoring guide, see
[`api/app/core/auth/README.md`](api/app/core/auth/README.md).

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
| `WAIT_DB` | unset | When `1`, the API entrypoint waits for `postgres:5432` before booting. Set to `1` for the default `docker-compose.yml`. |
| `FLASK_DEBUG` | unset | Enables Flask reloader + Werkzeug debugger. **Must stay unset (or `0`) in any prod-like compose.** |
| `FLASK_APP` | `wsgi.py` (dev) / `app:create_app` (prod) | Flask entrypoint. |
| `FLASK_CONFIG` | unset → `DevConfig` | Set to `production` to load `ProdConfig` (disables `SQLALCHEMY_ECHO`). Ignored if `create_app(config=...)` receives an explicit config. |
| `PORT` | `5050` | Port the API listens on. |
| `SQLALCHEMY_DATABASE_URI` | (set in `config.py`) | Postgres connection string. Override per environment. |
| `POSTGRES_DB` | `sample` | Used by the `postgres` image's `POSTGRES_DB` env var (creates the DB on first boot) and as the fallback in `DevConfig`. |
| `SECRET_KEY` | `''` | HS256 secret for `JwtBackend`. **Required in production** if the fork registers the `'jwt'` backend. |
| `FRONTEND_SECRET` | `''` | HMAC secret for `HashBackend`. Required if the fork registers the `'hash'` backend. |
| `HASH_VALIDITY_SECONDS` | `10` | Time window (seconds) accepted by `HashBackend` for a hash signature. |
| `CORS_ALLOWED_ORIGINS` | (dev) localhost:3000, :5173, :8080 / (prod) `[]` | Comma-separated list of allowed origins. Empty list disables CORS. Never use `*` in prod. |
| `RATELIMIT_ENABLED` | `false` | Enables `Flask-Limiter` with the default below. |
| `RATELIMIT_DEFAULT` | `100 per minute` | Per-IP limit when enabled. |
| `RATELIMIT_STORAGE_URI` | `memory://` | Storage backend. Use Redis (`redis://host:6379`) in prod with multiple gunicorn workers. |
| `PYTHONPATH` | `/api` | Set in the image so `flask` finds the app package. |
| `GUNICORN_WORKERS` | `2` | Number of gunicorn workers in prod. |
| `GUNICORN_TIMEOUT` | `120` | Per-request timeout (seconds) in prod. |

The full template with comments lives in [`.env.example`](.env.example).
Copy it to `api/.env` and fill in the values; `api/.env` is git-ignored.

## 6. Production deployment

Production runs the same Flask app through **Gunicorn** behind a reverse
proxy (nginx, ALB, Cloudflare, etc.). The contract is: the proxy joins the
`backend-network` Docker network and forwards traffic to `base-api:5050`.

### Image

`api/Dockerfile.production` builds on `python:3.12-slim`, installs
`requirements.txt`, copies the source, and runs `entrypoint.prod.sh`. It
exposes no port to the host — only to the `backend` network.

Differences vs the dev image (`api/Dockerfile`):

- `FLASK_DEBUG` is not set.
- `PYTHONUNBUFFERED=1` + `PYTHONDONTWRITEBYTECODE=1` for clean logs and no
  on-disk bytecode.
- No volume mount — code is baked into the image.
- `curl` is installed (needed by the healthcheck).
- Runs gunicorn, not `flask run`.

### Entrypoint

`api/entrypoint.prod.sh`:

1. Sets `FLASK_CONFIG=production` and `FLASK_APP=app:create_app`.
2. Runs `flask db upgrade` (Alembic migrations).
3. Executes gunicorn bound to `${PORT}` with `${GUNICORN_WORKERS}` workers.

### Compose

`docker-compose.prod.yaml` brings up the API only — **the database is not
included in prod**. The assumption is that Postgres lives elsewhere (managed
service, sibling container on the same network, etc.) and is reachable by
DNS name on the `backend` network.

Required setup before `up`:

```bash
docker network create backend-network
```

Then, in `api/.env`, set `SQLALCHEMY_DATABASE_URI` to the production database
URL. Example:

```env
PORT=5050
FLASK_CONFIG=production
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@db-host:5432/dbname
SECRET_KEY=<32-byte-hex>
CORS_ALLOWED_ORIGINS=https://app.example.com
```

Boot:

```bash
docker compose -f docker-compose.prod.yaml up --build -d
docker compose -f docker-compose.prod.yaml logs -f api
```

The service exposes two health endpoints:

- `GET /` — **liveness**. Returns `200` as long as the process is alive.
  Used by Docker's restart loop.
- `GET /health` — **readiness**. Returns `200` only when the database
  responds to `SELECT 1`; `503` otherwise. Used by load balancers and the
  `docker-compose.prod.yaml` healthcheck (`curl /health`).

The container is configured with `restart: always`.

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
- Known issues and roadmap: [`.ai-resources/issues/TECH_DEBT.md`](.ai-resources/issues/TECH_DEBT.md).
- All skills at a glance: [`.agents/skills/SKILL_INDEX.md`](.agents/skills/SKILL_INDEX.md).
- Writing a commit message? Use the
  [`commit-message`](.agents/skills/commit-message/SKILL.md) skill for the
  title format and body rules.
- Changed a model or generated a new migration? Use the
  [`update-schema`](.agents/skills/update-schema/SKILL.md) skill to keep
  `SCHEMA.md` in sync in the same commit.
