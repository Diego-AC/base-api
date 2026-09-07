---
name: create-module
description: Use this skill ALWAYS when the user asks to create, add, scaffold or generate a new domain entity, resource, endpoint, CRUD or module on a project built from the base-api template. Triggers on phrases like "create a Foo resource", "add a /users endpoint", "scaffold a new model", "I need a CRUD for X", "new module for X", even when the user does not say "module" explicitly. Generates the model + schema + repository + resource + route + Alembic migration in one go, following the Resource-Repository pattern.
---

# Create a new module

Generate a complete Resource-Repository scaffold for a domain entity named `Foo`.

## Inputs

Collect from the user (ask only if missing — do not guess):

| Field | Example | Required |
|---|---|---|
| Entity name (PascalCase) | `Foo`, `Order`, `UserProfile` | yes |
| Snake_case module name | `foo`, `order`, `user_profile` | derived from above |
| Custom columns (name + type + nullable + unique) | `name: str(120), unique, not null` | yes |
| Auth required? | yes / no (defaults to no) | optional |
| Relationships | `Foo has many Bar` | optional |

If the user only said "create a CRUD for orders" with no fields, ask for the
columns before scaffolding. Do not invent columns.

## Output

Produce these files, in this order, with no extras:

1. `api/app/models/<name>.py`
2. `api/app/schemas/<name>.py`
3. `api/app/repositories/<name>.py`
4. `api/app/resources/<name>.py`
5. Edit `api/app/models/__init__.py` (add the import)
6. Edit `api/app/routes.py` (register the resource)
7. Run the migration command and instruct the user to review the generated file

Use exactly the snippets under "Snippets". Substitute `<Name>` / `<name>`
placeholders. Do not paraphrase the snippets — copy them as the structural
skeleton and only edit the column definitions and class names.

## Hard rules

These come from `AGENTS.md` R1–R10. Violating any of them is a bug.

- **R3**: repositories own all DB access. Resources must not import `db` or `db.session`.
- **R4**: two schemas per entity — `BaseAutoSchema` for output, plain `Schema` for input. Never mix.
- **R5**: always `payload = schema.load(request.get_json() or {})` and pass `payload` to the repo. Never call `schema.load(payload)` and discard the result.
- **R6**: do not touch `core/errorhandlers.py` while scaffolding a module. Out of scope.
- Marshmallow has no `nullable=` kwarg. Use `allow_none=True` (or omit for required fields).
- HTTP errors inside resources are raised (`raise NotFound(...)`), never returned as `APIResponse.error(...)`.
- Soft delete is the default: `active = db.SmallInteger(... default=1)`. Do not call `_force_delete` unless the user explicitly asks for hard delete.
- Routes are plural (`/foos`, not `/foo`).

## Snippets

### 1. Model — `api/app/models/<name>.py`

```python
from sqlalchemy.sql import func
from ..extensions import db
from .base.mixins import TransactionalMixin


class <Name>(db.Model, TransactionalMixin):
    __tablename__ = '<names>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.SmallInteger(), nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    # custom columns (replace these)
    name = db.Column(db.String(120), nullable=False, unique=True)
```

Then add `from .<name> import <Name>` to `api/app/models/__init__.py`.

### 2. Schemas — `api/app/schemas/<name>.py`

```python
from marshmallow import fields, Schema
from .base.custom_schema import BaseAutoSchema
from ..models.<name> import <Name>


class <Name>Serializer(BaseAutoSchema):
    class Meta:
        model = <Name>
        load_instance = False


class Payload<Name>Schema(Schema):
    name = fields.Str(required=True)
    active = fields.Int(required=False, load_default=1)
```

Mirror the input schema fields to the model columns. Required fields in the
DB → `required=True` in Marshmallow. Optional → omit `required` and add
`load_default=<value>`.

### 3. Repository — `api/app/repositories/<name>.py`

```python
from .base.mixins import BaseRepository
from ..models import <Name>


class <Name>Repository(BaseRepository):
    def __init__(self):
        self.model = <Name>

    def find_by_name(self, name: str):
        return self.query.filter_by(name=name, active=1).first()

    def create(self, dataJson):
        entity = self.model(
            name=dataJson.get("name"),
            active=dataJson.get("active", 1),
        )
        entity.save()
        return entity.id
```

`get / get_all / update / delete` come from `BaseRepository`. Add only
domain queries here (`find_by_*`, `get_last`, ...).

### 4. Resource — `api/app/resources/<name>.py`

```python
from flask import request
from werkzeug.exceptions import NotFound

from ..schemas.<name> import <Name>Serializer, Payload<Name>Schema
from .base.custom_resource import BaseResource
from ..repositories.<name> import <Name>Repository
from ..core.responses import APIResponse


repository = <Name>Repository()
serializer = <Name>Serializer()


class <Name>Resource(BaseResource):
    def get(self, <name>_id: int):
        entity = repository.get(<name>_id)
        if entity is None:
            raise NotFound(description="<Name> not found.")
        return APIResponse.success(data=serializer.dump(entity))

    def post(self):
        schema = Payload<Name>Schema()
        payload = schema.load(request.get_json() or {})
        new_id = repository.create(payload)
        return APIResponse.success(data={"id": new_id}, status=201)
```

### 5. Route registration — `api/app/routes.py`

Append, do not rewrite:

```python
from .resources.<name> import <Name>Resource

def register_routes(api: Api):
    # ... existing routes ...
    api.add_resource(<Name>Resource, '/<names>', '/<names>/<int:<name>_id>')
    return api
```

### 6. Migration

```bash
docker compose exec api flask db migrate -m "add <names>"
```

Then tell the user explicitly:

> Open the generated file in `api/migrations/versions/` and **read it**
> before committing. Alembic autogenerate sometimes drops `unique`
> constraints, reorders columns, or misses enum changes. Apply with:
>
> ```bash
> docker compose exec api flask db upgrade
> ```

### 7. Smoke test

```bash
curl -s -X POST http://localhost:5050/<names> \
  -H 'Content-Type: application/json' \
  -d '{"name":"hello"}'

curl -s http://localhost:5050/<names>/1
```

Both responses must match `APIResponse` shape: `{message, status, data}`.

## Pitfalls

- **Discarding `schema.load(...)`** — the sample `versions` resource does
  this (TD-06). Do not copy it. The resource snippet above is the
  corrected version.
- **`fields.Int(nullable=False, ...)`** — no-op in Marshmallow. Use
  `allow_none=True` or omit.
- **Returning `APIResponse.error(...)` from a resource** — the error
  handler does this; the resource must `raise HTTPException` instead.
  See TD-01.
- **Autogenerate drops `unique=True`** — always re-read the migration
  file.
- **Forgetting to export the model** in `models/__init__.py` — Alembic
  will not see the table and the migration will be empty.

## Checklist

- [ ] Model inherits `TransactionalMixin` and lives in `models/<name>.py`.
- [ ] Model exported from `models/__init__.py`.
- [ ] Two schemas: `<Name>Serializer(BaseAutoSchema)` + `Payload<Name>Schema(Schema)`.
- [ ] Repository extends `BaseRepository`; adds only domain queries.
- [ ] Resource extends `BaseResource`; `schema.load(...)` result captured.
- [ ] Errors raised as `HTTPException`, not returned as `APIResponse.error`.
- [ ] Route registered in `routes.py` (plural collection).
- [ ] Alembic migration generated, reviewed and applied.
- [ ] `curl` smoke test returns `APIResponse` shape.
