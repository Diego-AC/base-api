---
name: commit-message
description: Use this skill ALWAYS when the user is about to commit, asks to write a commit message, asks for a commit title, says "commiteá", "armame el commit", "qué pongo como mensaje", "prepará el commit", or shows a `git diff` / list of changed files and asks how to describe it. Produces a Conventional-Commits-style title (type + verb + short description) and an optional narrative body that explains the *why* of the change, not the *what*.
---

# Commit message

Produce a commit title, and a body only when the change is complex.

## Inputs

If the user has not already shared them, inspect or ask for:

| Field | Source |
|---|---|
| Staged / unstaged diff | `git diff --staged` (preferred) or `git diff` |
| Recent commits for tone reference | `git log --oneline -10` |
| Any extra context the user offers | free text |

Do **not** ask the user to retype what `git status` already shows. Read the
repo state and only ask if the intent of the change is genuinely ambiguous
(e.g. a multi-area diff that could be split, or a rename that could be a
`Refactor` or a `Fix`).

## Output

Always produce exactly this shape:

```
<Title>

[Optional body — only when the change is complex]
[Blank line between paragraphs if more than one.]
```

No bullet lists in the body. No "Added file X" / "Modified Y" lines. The diff
already shows what changed; the body exists to explain why.

## Title format

`<Type>(<optional scope>): <verb in imperative, lowercase> <short description>`

### Allowed types

Use the first that fits. Don't invent types.

| Type | When |
|---|---|
| `Feat` | New user-visible feature, new endpoint, new module, new capability. |
| `Fix` | Bug fix. Behaviour now matches what was intended or documented. |
| `Refactor` | Internal change with no behaviour change. Renames, restructures, dedup. |
| `Change` | Behaviour change to existing functionality that is not a bug. Policy, config, default values. |
| `Perf` | Performance improvement with no behaviour change. |
| `Docs` | Documentation only — README, comments, skills, AGENTS.md, no code change. |
| `Test` | Adding or fixing tests only. |
| `Build` | Build system, `Dockerfile`, `requirements.txt`, CI/CD, Alembic. |
| `CI` | Pipeline / workflow files only. |
| `Style` | Formatting, whitespace, imports order — no logic change. |
| `Chore` | Maintenance that doesn't fit the above (deps bump, dead code removal, repo hygiene). |

### Rules for the title

- **Imperative mood**, lowercase after the colon: `add`, `fix`, `move`, `split`,
  `wire`, `rename`, `drop`. Never `added`, `adding`, `fixes`.
- **No period** at the end.
- **~50 chars** ideal, hard cap ~72. If the title is too long, the description
  is doing too much — move it to the body.
- **Scope is optional**. Use it when the change is clearly scoped to one layer
  or area: `Feat(versions): add last-version endpoint`,
  `Refactor(repositories): unify create signature`. Skip it for cross-cutting
  changes.
- If the diff mixes two unrelated concerns, **split the commit**. Tell the
  user explicitly and propose two separate titles.

### Examples of good titles

```
Feat: add /versions/last endpoint
Fix: raise NotFound when last version is missing
Refactor(repositories): make create accept kwargs
Change: default new entities to active=1
Docs: rewrite README sections 1-6 in English
Build: bump Postgres to 16-alpine
Chore: drop unused _force_delete from mixin
```

## Body — only when the change is complex

### When to include a body

Include a body if **any** of the following is true. Otherwise stop at the title.

- The change spans more than ~3 files or more than one layer
  (e.g. model + schema + repo + resource + migration).
- It introduces a new pattern, dependency, or breaking change.
- It fixes a non-obvious bug where the cause is not self-evident from the diff.
- It makes a design decision the reviewer might question.
- It deprecates, removes, or renames something public.

A typo fix, a one-line tweak, a rename of a local variable, a dependency bump
without surprises — **title only**.

### What the body is for

The body is the **commit's story**. It explains:

1. **Why this change exists.** What was the problem, smell, missing capability,
   or risk that prompted it? Frame it from the user's or the next developer's
   perspective, not the code's.
2. **Why this approach over the alternatives.** When there's a real trade-off
   (e.g. "kept the placeholder auth rather than picking a provider", "didn't
   fix the error handler in the same PR to keep blast radius small"), say so.
3. **What it sets up next.** If there's a known follow-up, link it
   (`TECH_DEBT.md` entry, `TD-XX`, a future PR). Don't enumerate the
   follow-ups — just point to them.

### What the body must NOT do

- ❌ List the changed files. (`git show --stat` does that.)
- ❌ List the new functions / classes. (The diff does that.)
- ❌ Use bullet points for "what changed". That belongs in a PR description
  or a changelog, not a commit body.
- ❌ Repeat the title in different words.
- ❌ Use phrases like "this commit", "this PR", "added X to Y file". Write in
  the timeless register of an engineering decision: the problem, the
  reasoning, the consequence.

### Voice and length

- Write in **plain prose**, one or two short paragraphs. Usually 3–8 lines.
- Sentences flow. No headings inside the body.
- Past or timeless present. Avoid future tense.
- If you genuinely cannot write more than one paragraph, prefer the title
  alone over padding.

### Body template (use as a checklist, not as literal output)

> *One paragraph framing the problem or motivation the way you'd explain it
> to a teammate in a code review.* Then, *one paragraph (optional) on the
> approach chosen and any trade-off the reviewer should know about.* Then,
> *one short sentence (optional) pointing to follow-ups — a `TD-XX`, a link,
> or "see TECH_DEBT.md".*

## Pitfalls

- **Listing changes in the body.** If the body starts with "Added...",
  "Modified...", "Created...", "Updated..." — stop, delete the body, and
  keep only the title.
- **Title longer than ~72 chars.** The title is a label, not a summary. If
  you need a summary, that's the body.
- **Mixing concerns in one commit.** A diff with `models/`, `repositories/`
  and `requirements.txt` is usually two commits. Suggest the split.
- **Picking the wrong type.** "I refactored the auth" is `Refactor` only if
  behaviour is identical. If you also changed the API surface or default
  behaviour, it's `Feat` or `Change`.
- **Burying the type.** `<Type>` is always the first token. Don't write
  `[Feat] add foo` or `feat:` (lower-case) — keep the canonical capitalisation
  for grep-ability across the log.
- **Using Spanish verbs in an otherwise English repo (or vice-versa).**
  Match the dominant language of the recent log (`git log --oneline -10`).

## Workflow

1. Run `git status` and `git diff --staged` (or `git diff` if nothing staged)
   to see what actually changed. Don't trust the user's summary blindly.
2. Run `git log --oneline -10` to match the project's tone and language.
3. Decide the type from the table above.
4. Decide if a body is needed (see "When to include a body").
5. Write the title.
6. If a body is needed, write 1–2 paragraphs of *why*, not *what*.
7. Show the user the result as a fenced block and ask: "te queda bien o lo
   ajusto?". Do **not** run `git commit` unless the user asks explicitly.
