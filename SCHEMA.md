# Schema

Quick reference for the database models: **what exists, what it stores, and how it relates**.

The DDL lives in `api/migrations/versions/` — don't duplicate it here.
Keep this file in sync with the models in the **same commit**.

For the sync procedure: [`.agents/skills/update-schema/SKILL.md`](.agents/skills/update-schema/SKILL.md).

---

## Index

| Table | Purpose |
|---|---|
| `versions` | Sample entity used as the canonical example for the Resource-Repository pattern. Tracks a description and a soft-delete flag. Replace or extend when starting a real project. |

Append rows here as the project grows. Do not renumber.

---

## Tables

### `versions`

Mixins: `TransactionalMixin`. Soft delete via `active = false`.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | `INTEGER` | NO | — | PK, autoincrement. |
| `description` | `VARCHAR` | NO | — | Free-form. No length declared. |
| `active` | `BOOLEAN` | NO | `true` (Python) | Soft-delete flag. Indexed (`ix_versions_active`). Default applied at the SQLAlchemy layer. |
| `created_at` | `DATETIME` | YES | `now()` | |
| `updated_at` | `DATETIME` | YES | `now()` on update | |

Relations: none.
Indexes: PK + `ix_versions_active` on `(active,)`.

---

## Migrations

Tool: Flask-Migrate (`flask db ...`). Directory: `api/migrations/versions/`.

| Revision | Description | Created |
|---|---|---|
| `9e681dd9c27f` | initial: create `versions` | 2024-10-18 |
| `f3ea58733afb` | convert `versions.active` from `SMALLINT` to `BOOLEAN` (using `active <> 0`) and add `ix_versions_active` | 2026-10-17 |
