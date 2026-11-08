# Write docs for an existing codebase

Use this when a codebase has little or stale documentation and the user asks for
durable docs, not a one-off answer. The docs are written from traced source, so each
claim can be checked and a later [drift check](../../architect/references/design-drift.md)
can compare them with the code.

## What to write

Keep it to what a new engineer or agent needs before changing code:

| Document | Contains |
| --- | --- |
| Overview | What the system does, its main parts and how a request or job moves through them |
| Module map | Each part's owner, entry points, the state it owns and what it may depend on |
| Key flows | Three to five important paths, each traced entry point to result, with one failure path |
| Running it | How to build, test and run it locally; run commands only when authorized, otherwise mark each step source-derived |

Every flow step and owner claim carries a file and symbol anchor. Mark each claim
observed (you ran it) or source-derived (you read it). Write what you could not
establish as an open question, never a guess.

## How to run it

1. **Ask where docs live** in this project. Use its existing docs folder and
   conventions; write into a target repository only within the user's scope.
2. **Trace before writing,** with this skill's method. Delegate wide reading to
   scouts within the harness limits; the lead writes the docs.
3. **Draft one document at a time** and pause for the user's corrections before the
   next. They know intent the code cannot show; route intent questions to
   [why](../../why/SKILL.md).
4. **Update instead of duplicating.** When docs exist, extend or correct them in
   place, and report what was stale.

Do not document every file, paste code, or describe intent the source does not show.

Reviewed inspiration, observed 9 November 2026:
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model/tree/e9e1f06aa4e26e95cd4ed37210a0632202c429e9)
(Apache-2.0). Independently written; no upstream text, prompts or tooling imported.
