# Install Opengrep from the pinned source

The library pins the engine in [source-pin.json](source-pin.json): release `v2.0.0`, commit
`526deafe6f0519c272bbee316fea8df26dd85dfa`, licence LGPL-2.1. The engine is copyleft, so its source stays
outside this repository: it is downloaded into the ignored `orbyn-references/` folder and built there. Nothing
from it is copied into the library.

## What the build needs (read from the pinned source's own install notes)

- OCaml 5.5.0 with `opam` and `dune`
- a C toolchain with the PCRE and gmp libraries
- `make` and `git`

## Steps

1. **Check the machine without changing it:** `python3 scripts/opengrep_source.py status` lists the pin, whether
   a reference copy exists and which tools are missing. It installs nothing.
2. **Read the source if you want to** (no code runs): `python3 scripts/opengrep_source.py reference` downloads
   the pinned commit as an archive into `orbyn-references/opengrep/opengrep/<commit>/` with a `<commit>.json`
   receipt. It refuses unsafe archive paths, skips links, checks the commit id GitHub records in the archive against the pin
   when the archive has one, and refuses to write if `orbyn-references/` is not ignored by Git. An interrupted run
   leaves a folder with no receipt: the next run refuses and tells you to move it aside.
3. **Build only on request:** `python3 scripts/opengrep_source.py build --yes` clones into
   `orbyn-references/opengrep-opengrep/build/<commit>/`, checks out the exact pinned commit (it stops if the
   checked-out commit differs), initialises the submodules, runs `make setup` and `make core`, and prints the path
   of `bin/opengrep`. `make setup` installs OCaml packages through `opam`, so this step runs upstream build scripts
   and needs `--yes`. The commit and the submodule commits are pinned; the opam packages `make setup` downloads are not, so a build trusts the network at that step. The helper refuses a references folder Git does not ignore, and an existing build folder that is not a clean checkout; it never deletes anything, so move a stale folder aside yourself. A source checkout with a nested `.git` is held, not removed, by the workspace cleanup.
4. **Verify the binary:** `bin/opengrep --version`, then write a one-line rule with an `ok` and a `ruleid` case
   and run `opengrep validate` and `opengrep test` ([rule writing](rule-writing.md#tests)). Record the version.

Do not install through a package manager or an installer script, and do not install a toolchain as a side effect of
a task: if tools are missing, report which and stop.

## Keeping the pin current

A newer release is a lead, not an update. Use the [upstream review](../../orbyn-upstream-review/SKILL.md) method:
resolve the full commit, read the licence at it, review the diff, and change the pin and `source-pin.json` in
one reviewed change. The pin file is the single place the commit is named.

## Limits

The build has not been run by this skill's authors (the build tools were not on the machine that prepared it).
The steps come from reading the pinned source, not from a successful build, and Windows is not covered here:
the upstream project ships Windows binaries and this page does not document a Windows source build.
