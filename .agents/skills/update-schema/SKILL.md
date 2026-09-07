---
name: update-schema
description: Use this skill ALWAYS when the user has just changed a SQLAlchemy model, added a new model, added or modified a relationship, generated an Alembic migration, or asks to "update SCHEMA.md", "refresh the schema doc", "sync the schema", "document the new model", "agregué una relación", "actualizá el schema". Keeps SCHEMA.md in sync with the actual models and migrations in the same commit that changes them.
---

# Update SCHEMA.md

Keep `SCHEMA.md` aligned with the real state of `api/app/models/` and
`api/migrations/versions/`. Targeted edits only — never rewrite the file.

## Inputs

Read these before editing anything:

| What | Where |
|---|---|
| Current models | `ls api/app/models/*.py` (skip `__init__.py`, `base/`) |
| Columns + relationships per model | open each file, read `db.Column(...)` and `db.relationship(...)` |
| Current Alembic head | `ls api/migrations/versions/*.py` |
| Most recent migration | read it: `revision`, `down_revision`, `Create Date`, what `upgrade()` does |
| Current `SCHEMA.md` | read it fully before editing |

Do not guess column types or relations. If a model's intent is ambiguous
(e.g. a `JSON` column with no shape comment), ask the user.

## `SCHEMA.md` has exactly three sections

1. **Index** — table of `Table | Purpose`.
2. **Tables** — one subsection per table, each with: mixins, column table
   (`Column | Type | Nullable | Default | Notes`), `Relations:` line,
   `Indexes:` line.
3. **Migrations** — table of `Revision | Description | Created`.

That's it. Don't add sections. If you feel the need for diagrams,
conventions, "how this grows" prose — stop. That's content for `AGENTS.md`
or `README.md`, not `SCHEMA.md`.

## Procedure

### 1. Read the current state

Build an internal picture of which tables exist, which are new, which got
columns or relations added/dropped, what the latest migration does.

### 2. Update Index

Append a row: `| <table> | <one-line purpose> |`.

- **New model**: append. Do not insert alphabetically.
- **Removed model**: do not delete the row. Change the purpose cell to
  `<purpose> (deprecated YYYY-MM-DD)`. The audit trail matters.
- **Renamed model**: edit the row in place; mention the rename in the
  commit body.

### 3. Update Tables

For each changed table, edit its subsection in place.

- **New column**: add a row in declaration order (top-down as in the model).
- **Dropped column**: keep the row, mark `(dropped YYYY-MM-DD)` in Notes.
  Add the replacement row below it if any.
- **Renamed column**: keep both rows; old one becomes
  `(renamed to <new> on YYYY-MM-DD)`.
- **Type change**: edit the Type cell. If non-trivial (e.g. `VARCHAR` →
  `JSONB`), add a one-line note directly under the table.
- **New index / constraint**: bullet under `Indexes:` — `<column> (<type>)`.
- **New relation**: edit the `Relations:` line to
  `<child_col> → <parent_table>.<pk> (<ondelete>, nullable=<yes/no>)`.
  Multiple relations → one bullet per line.
- **Removed relation**: keep as `(deprecated)`.
- **Changed mixin**: edit the `Mixins:` line.

Document intent, not aspiration. If the model has a smell, document what
the code *is*; track the fix in `TECH_DEBT.md`.

### 4. Update Migrations

Append a row: `| <revision> | <description> | <YYYY-MM-DD> |`.

- Revision: from the migration's `revision = '...'` line.
- Description: imperative phrase (`add users`, `add foos.active_index`).
- Created: from the migration's `Create Date` line if present;
  otherwise today's date.

Sort rows oldest → newest. Do not reorder existing rows.

### 5. Sanity check

Before showing the diff:

- Every model (excluding `base/`) has a row in Index and a Tables subsection.
- Every migration has a Migrations row.
- No fabricated data — every cell came from reading the code or the
  migration.
- No new sections introduced.

## Pitfalls

- **Rewriting the whole file.** Targeted edits only.
- **Inventing types or defaults.** If the model says `db.String()`,
  write `VARCHAR` — not `VARCHAR(255)`. The latter is a guess.
- **Reordering existing rows.** Append-only for Index and Migrations.
  Existing order = insertion order = history.
- **Adding new sections.** No diagrams, no "conventions", no
  meta-prose. `SCHEMA.md` stays a flat reference.
- **Committing `SCHEMA.md` in a separate commit from the migration.** They
  belong together. If you find yourself about to commit `SCHEMA.md` alone,
  stop and ask whether the corresponding model change is also staged.

## Workflow

1. Read current state.
2. Identify what changed.
3. Edit Index, Tables, Migrations as needed.
4. Sanity check.
5. Show `git diff SCHEMA.md` to the user and ask before committing.
