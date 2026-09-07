# Skills Index

This template ships with skills under `.agents/skills/`. Each skill is a
single `SKILL.md` file inside its own folder.

The goal of these skills is to give AI agents (and humans) a **reusable,
actionable procedure** — not a knowledge dump. The rules of the project live
in `AGENTS.md` and `README.md`; the skills say *what to do step by step*.

## Available skills

| Skill | Use it when |
|---|---|
| [`create-module`](./create-module/SKILL.md) | You are adding a new domain entity (e.g. `User`, `Order`) and need to scaffold the full Resource-Repository module: model → schema → repository → resource → route → migration. |
| [`commit-message`](./commit-message/SKILL.md) | You are about to commit and need a Conventional-Commits-style title (and body when the change is complex) that explains the *why*, not the *what*. |
| [`update-schema`](./update-schema/SKILL.md) | You changed a model, added a relationship, or generated a new Alembic migration, and need to keep [`SCHEMA.md`](../../SCHEMA.md) in sync in the same commit. |

## Conventions and rules (not skills)

These are **knowledge/rules**, not procedures. They live elsewhere:

- [`AGENTS.md`](../../AGENTS.md) — operating rules for AI agents (R1–R10).
- [`README.md`](../../README.md) — stack, architecture, quickstart.
- [`SCHEMA.md`](../../SCHEMA.md) — living index of database models, columns and relations.
- [`.ai-resources/issues/TECH_DEBT.md`](../../.ai-resources/issues/TECH_DEBT.md) — known issues.

If you find yourself writing a skill that is mostly rules and prose, stop:
that's content for `AGENTS.md`. A skill should produce concrete output
(files, commands, patches).
