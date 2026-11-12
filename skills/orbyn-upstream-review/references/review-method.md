# Upstream review: baseline, watcher issues and gap table

Detail for the [entry skill](../SKILL.md); its rules and approval steps apply. This
file holds only the mechanics the entry leaves out.

## Establish the actual baseline

Inspect manifests, provenance, snapshot records, lockfiles and source bytes; an
adaptation's original source revision does not cover every later reviewed change.
Prefer a bounded subtree comparison over unrelated repository history. Account for
pagination and API file limits: a truncated compare response is not a complete
change inventory.

## Act on a watcher issue

`scripts/upstream_watch.py` runs weekly from `main` and keeps one `upstream-update`
issue per pinned source: pinned and candidate commits, changed files inside what we
use, licence state and affected skills. It reads API metadata only. A closed issue
stays closed until the facts change.

`upstream-licence-change` means a licence file changed or GitHub's detected licence
differs from our record. A compare marked truncated lists at most 300 files; its
affected skills still come from Git object ids. A snapshot whose `source_path` values
start below the repository root records that folder in `source_root`.

## Gap table

| Gap | Upstream source (path at commit) | Our owner | Proposed change | Size |
| --- | --- | --- | --- | --- |
| What we lack, in a few words | `path` at the candidate | skill and reference | Adapt, already covered, skip and why | S, M or L |

One row per gap, including the ones you recommend skipping, so the reader sees the
whole picture.
