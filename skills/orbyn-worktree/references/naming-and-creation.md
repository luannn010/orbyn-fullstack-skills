# Name, create and verify a worktree

Detail for the entry skill's [reuse](../SKILL.md#reuse-before-cloning-or-replacing),
[sibling location and names](../SKILL.md#sibling-location-and-names) and create-and-verify steps. The rules there still apply; this file holds the mechanics.

## Reuse checklist

Beyond the entry's reuse rules, inspect the canonical repository and its remotes, and
host attachments and bindings, not only registered trees and any reference cache.
Confirm that no active session still holds a clean directory before reusing it.

## Sibling location and names

For a primary clone `<parent>/<repo>`, the default root is its sibling
`<parent>/<repo-slug>-wt/`. Use a stable lowercase hyphenated repo slug; reuse an
existing established sibling root rather than creating a case-only alternative.
Each worktree has one direct child directory named for its purpose slug, not the
branch's slash-separated path:

```text
orbyn-fullstack-skills/repo/
  orbyn/                         primary clone
  orbyn-wt/
    task-rescheduling/           feat/task-rescheduling
    save-retry/                  fix/save-retry
    worktree-policy/             chore/worktree-policy
```

Targets use the library-root ignored `repo/` workspace by default under the
[nested repository contract](../../orbyn-setup/references/repository-workspaces.md):
`orbyn-fullstack-skills/repo/widget` uses sibling `repo/widget-wt/<purpose>/`.
An explicit user location or an established consuming-project policy wins.

Use lowercase letters, digits and hyphens for a short directory slug, normally
under 64 characters, and branch prefixes such as `feat/`, `fix/`, `chore/`, `docs/`
or `refactor/`. Avoid path separators, traversal, spaces, Windows device names and
case-only distinctions.

If a colliding path/branch is unrelated or still owned, choose a distinct purpose or
a suffix such as `-2` (the entry's collision rules apply).

## Create and verify the selected checkout

The entry holds the base, branch-flag and verification rules. Mechanics: continue an
existing task/PR from its actual branch or reviewed commit; for new work use the
project's verified default branch/ref, not an unrelated current feature branch.
Reuse an existing branch with `git worktree add <path> <branch>` after
ownership/checkout inspection. Worktrees share Git objects and may still share
databases, ports, fixtures or external services, so assign those separately.
