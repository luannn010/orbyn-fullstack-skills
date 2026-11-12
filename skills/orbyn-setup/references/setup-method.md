# Setup method details

Detail for the numbered method in the [entry skill](../SKILL.md). The rules there
apply; this file holds only the mechanics, notes and recovery text the entry omits.

## Steps 5, 6, 7 and 9 in detail

Only what the entry's numbered steps leave out; the steps and their rules stay there.

5. **Search roots.** Refresh relevant locations when paths, rules or available context
   change. Check [ripgrep readiness and fallback](offline.md#ripgrep-readiness-and-fallback)
   in the actual agent environment before relying on `rg`; with a missing tool, use
   bounded inspection with an available alternative.
6. **Target guidance.** The `check` output reports overlapping names so you can
   distinguish target-specific rules from shared methods instead of installing a
   competing copy. It also registers the target as a memory project unless memory is
   opted out.
7. **Root the session.** Inspect the host's actual discovered guidance where supported;
   otherwise read the required files directly. Parent-directory placement alone does
   not prove a host loaded either instruction set.
9. **Report.** Distinguish located files, returned contents, observed
   originating-request inclusion and actual execution enforcement.

## Setup notes the entry leaves out

- Reading a target's existing context map is optional and read-only; use
  [offline resources](offline.md). No map or namespace is required.
- To tune one repository, the owner may add `.orbyn/harness.json` there (a target
  change needing normal authority) or a local `repo/.harness/<target-slug>.json`.
  `python3 <orbyn-workflow directory>/scripts/harness.py resolve --target <target>`
  reports the result. `harness.py setup` writes only the ignored local or in-place
  owner file under `repo/.harness/`.
- Host model definitions are optional library configuration governed by its model
  policy; use permitted direct work rather than silently substituting models.
- Reading groups in [presets.json](../assets/presets.json) help choose relevant methods;
  they no longer control installation or hide source files.

## Resume after a workspace or runtime change

After migration/resumption, a failed working directory or a runtime mismatch, reconcile
the actual selected checkout with the host's saved session binding where observable. An
explicit command workdir, a moved folder or project membership does not prove the
session was rebound. Use a supported authorized host mechanism if needed; otherwise
report the stale/unknown binding, use a valid explicit workdir for supported work and
retain that distinction. Do not recreate a deleted checkout or rewrite global session
settings/PATH to hide the problem.

Inspect the next required command's documented runner/version and resolve a compatible
already-installed runtime in the actual execution environment before an expensive run.
A harmless version/capability check is sufficient when available. Do not execute
untrusted setup hooks or install a runtime implicitly. If no runtime is supported,
report the dependent check blocked and continue independent work. Reuse current matching
readiness evidence. This is conditional recovery, not a full setup ritual on every
action or a reason to repeat passed suites.
