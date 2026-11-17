# Write and layer a project's AGENTS.md files

Use when a project asks to write, split or tidy its agent instruction files. Setup
itself writes none of them; this is the project's own authorized task, and the
project's existing files and conventions win.

## Choose the levels

What each level holds is in [rules beside the code](project-skills.md#rules-beside-the-code-they-govern):
standing orders at the root, folder-only rules in a subtree file, detail in READMEs,
maps and decision records. Add a subtree `AGENTS.md` when a folder's work needs
rules the rest of the repository must not follow: its own test command, language
or boundary. A test or tooling folder can have one for how its suites are run and
how fixtures are kept. A single-package repository usually needs only the root.

## Write each file

- Lead with the rules a change is most likely to break; some hosts cap how much of
  a long file they load.
- One rule per bullet, stated as an instruction, with a command or short snippet
  where a description would leave room to guess.
- Link to the README, map or decision record that holds the detail.

Leave out, and say where it goes instead:

| Content | Belongs in |
| --- | --- |
| Style a formatter or linter already enforces | That tool's config |
| Pull request description layout | The pull request template |
| One contributor's habits | Their own user-level instructions or memory |
| Credentials, internal hostnames, anything unsafe to commit | Nowhere in the repository |
| How a rule was discovered | The PR or issue that proved it, linked from the rule |

## Record a fact that cost several attempts

Write one short paragraph a newcomer cannot get wrong: what to do, what breaks if
they skip it, and the fix already disproven, with its PR or issue. "The desktop
build is flaky" helps nobody; "Run `cargo build` before `pnpm dev`: the app copies
the sidecar binary at startup, so `pnpm dev` alone runs last week's binary (#231)"
does. Delete the paragraph when the code that made it necessary is gone.

## Keep the levels from disagreeing

Hosts differ in which files they load and in what order, so never rely on a
precedence order ([action scope](action-scope.md#separate-instruction-lookup-from-code-search)).
Write the levels so they agree: a subtree file adds rules for its folder and does
not restate the root. When a folder needs a different convention, the subtree file
says so for that folder only. A subtree file never relaxes a safety, permission or
review rule from above; if a folder seems to need that, raise the conflict with the
owner instead ([instruction conflicts](../SKILL.md#resolve-instruction-conflicts)).

A host that reads only its own filename (for example `CLAUDE.md`) gets a one-line
pointer file beside the `AGENTS.md`, importing it where the host supports imports
(`@AGENTS.md`), never a second copy that can drift. Add pointer files only where the
project owns its instructions or its maintainers accept host files; in someone
else's repository, keep host discovery paths unchanged. Nesting alone does not prove
a host reads a subtree file, so an agent working there still reads it explicitly.

## Keep it true

Change the instruction file in the same change as the code that makes a rule true or
false. When agents repeat a mistake, add the rule with an example, or turn it into a
check that fails ([structural prevention](../../architect/references/principles/encode-lessons-in-structure.md)).
Delete a stale rule at once: agents follow it confidently.

## Worked failure

A monorepo keeps one root `AGENTS.md` holding "use `vitest`" for the web app and
"use `pytest`" for the API. An agent fixing an API bug runs `vitest` from the root,
sees green and reports done while the Python tests never ran. Fix: the root names the
packages and the command that tests everything; `apps/web/AGENTS.md` and
`services/api/AGENTS.md` each name their own test command; where the project uses a
host that reads `CLAUDE.md`, each folder gets one containing `@AGENTS.md`.

## Source

Adapted ideas from SSW Rules, [Do you write an AGENTS.md?](https://www.ssw.com.au/rules/write-agents-md),
observed 17 November 2026. Wording, structure and examples are our own.
