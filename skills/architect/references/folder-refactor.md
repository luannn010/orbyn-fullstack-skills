# Refactor a whole app's folder architecture

Use this when a codebase has outgrown its layout: giant files, cycles between
features, deep imports into other features' internals, duplicated helpers, or
business logic in the transport layer. It turns [capability ownership](vertical-codebase.md)
into a delivery plan. A single misplaced module needs a move, not this.

## 1. Map before you move

Measure with the compiler and real tools, never by matching names. A scout can run
the mechanical part; the lead decides the target. Record each number with the base
revision so later units can show progress.

| Measure | How | Shows |
| --- | --- | --- |
| Largest files and sections | Line counts per file; count of top-level types, functions or rules in each | Files that hold several capabilities |
| Import graph | The compiler's or bundler's resolved imports (for example a dependency-graph tool), per feature | Cycles and deep imports into another feature's internals |
| Duplicate helpers | Search by behavior (formatters, key handlers, path lookups, process spawns), then confirm with the call sites | Logic that wants one owner |
| Unused exports | The compiler or a dead-export tool that resolves imports; never a text search. Exclude anything a published package or crate exposes | Code that can go before it is moved |
| Layer leaks | Business rules found in route handlers, IPC or transport adapters | Logic to move behind its owner |
| Global styles | Selectors in shared stylesheets that target one feature | Styles to co-locate |

## 2. Write the target rules

Agree a short rule set with the owner before moving anything. These are defaults to
tune to the project, not fixed numbers. A typical set:

- One folder per capability, with sub-folders per topic once it grows.
- One front door per feature (`features/<x>/index.ts`, a Rust module's `mod.rs` or
  `lib.rs`) exporting only its public surface. It is the only import other features
  may use, and it never re-exports everything.
- Dependencies point one way, for example app → features → shared ui/lib/state → api.
  Shared rendering two features both need moves to a shared feature, which breaks
  the cycle instead of hiding it.
- Styles, tests and data hooks live beside the component they serve.
- A soft size cap (for example about 600 lines): past it, a file becomes a folder.
- One name, one meaning across the app (for example Page = a route, Panel = a side-
  panel tab, Dialog = a modal).
- Transport layers (HTTP handlers, IPC commands) validate, call the owner and map the
  result; they hold no business rules.

## 3. Order the units

Split the move into behaviour-neutral units, each its own PR:

1. Delete unused exports and dead files first; they only add work to every later unit.
   Keep anything with external consumers: a published package or crate's exports are
   public API even with no callers in this repository.
2. Extract shared pieces that break cycles (the shared feature, single helpers for
   each duplicated behavior), then move features from the leaves of the import graph
   inward, so each unit's dependencies are already in place. A giant shared leaf,
   such as a contracts file, can be split early behind re-exports that keep its paths.
3. Split giant files within each feature last, by the sections the map found.
4. Lock by area: one unit owns a folder while it is open, and parallel work avoids it
   or waits. Rebase each unit on the latest base before review.

Keep pure moves and renames apart from edits, and list the moves in
`.git-blame-ignore-revs` so blame still finds the real author. A squash merge folds
both into one commit, so land a pure move as its own PR (or merge without squashing),
and record the SHA as it exists on the base branch after the merge. Keep generated names, public API names and persisted keys unchanged unless
a migration owns the change. Each unit passes the existing build and tests with no
behavior change. Where tests are thin, add characterization tests for the area first
([tdd](../../tdd/SKILL.md)); a fix found along the way gets its own PR.

## 4. Enforce the rules

Add checks for import direction (no deep imports, no forbidden layers), file size and
unused exports. Start each as a warning across the codebase, and turn it into an error
for a unit once that unit is done, so finished areas cannot regress while the rest is
still moving. Report counts per unit against the map's baseline.

## Return

The map with its base revision, the target rules, the ordered unit list with owners
and locks, the enforcement plan, and what each finished unit changed in the counts.

Synthetic example: a web app's shared types file holds hundreds of types in thousands
of lines, an orders feature and a billing feature import each other through a shared
invoice view, and several date formatters exist. The map records all three. The plan
deletes internal unused exports, splits the types file behind re-exports early, extracts
the invoice view and one date formatter into shared features, then moves each feature
behind its front door.
