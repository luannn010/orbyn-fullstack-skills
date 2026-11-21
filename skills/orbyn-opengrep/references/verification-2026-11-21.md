# Opengrep built from source and tried, 2026-11-21

Record for the `orbyn-opengrep` skill. One run by one person on one machine; static expectations elsewhere.

## Environment

macOS 27.2.1 on Apple Silicon. Homebrew: opam, pcre2, gmp, libev, coreutils, gettext, bash 5.3, pkg-config. OCaml 5.5.1,
dune 3.25.0 in an isolated opam root under the ignored `orbyn-references/` folder. Engine: release `v2.0.0`, commit
`526deafe6f0519c272bbee316fea8df26dd85dfa`, built by `scripts/opengrep_source.py build --yes`.

| Phase | Wall time |
| --- | --- |
| Homebrew packages | about 4 min |
| opam init and OCaml 5.5.1 switch | about 3 min |
| dune, clone, submodules, `make setup`, `make core` | about 7 min |
| Total | about 15 min; opam root 1.1 GB, build tree 3.0 GB |

First attempt failed before anything was installed because `~/Library/Caches/Homebrew` was owned by root; a private
`HOMEBREW_CACHE` fixed it without changing ownership. `opengrep --version` prints `2.0.0`.

## Flag and behaviour checks (35 checks, synthetic rules, throwaway folders)

Every command ran in a macOS sandbox that kills the process on any network attempt (a control showed it kills
`curl`). **31 passed and none was killed**, so scans, tests, baselines, autofix and interfile runs make no network
attempt with local rules. Passed: `--error` exit 1 with findings and 0 without; `--json` and `--sarif` output;
`--baseline-commit` shows only findings not present at the commit, aborts outside Git and on an unknown commit, and
**does not abort on unstaged changes** (this corrected an earlier claim); `nosemgrep`, `nosem` and `noopengrep`;
`--severity`, `--include`, `--exclude`; `--timeout`, `--max-memory` and the rule options with
`--allow-rule-timeout-control`; `--autofix` rewrites the file, `--dryrun` and the default scan do not; duplicate rule
ids keep one rule; the unquoted `shell: true` pattern fails and the quoted one parses; taint rule with a sanitizer;
`--dataflow-traces`; interfile finds the cross-file flow with `taint_interfile` plus `--enable-interfile` and finds
nothing, with a warning, without the flag; `--taint-intrafile`; `--interfile-depth`; `show dump-interfile-graph`;
`opengrep test` passes with matching annotations and fails on a missed `ruleid`; a `p/` ruleset fails offline.

Two checks failed, for one reason found afterwards: **`opengrep validate` is not local.** It downloads
`https://semgrep.dev/c/p/semgrep-rule-lints` to lint the rule (its source says it needs the network), so it was killed
in the sandbox. With the network allowed it crashed with a bus error (exit 138) after the download, with a default and a
larger stack; whether the release binary does is unknown. Four read-only requests for that public ruleset were made while
diagnosing this.

## Trial on a real project (Orbyn Engineering at b9c0174d9, read-only)

Eight starter rules written from the project's risk list, each proven with a `ruleid` and an `ok` case (8 of 8 passed
offline). Scan of `crates`, `desktop` and `web/src` excluding tests and generated files: 1,252 files in 1.9 s, no network
attempt, **69 findings, all Rust**: 35 `unsafe` blocks, 18 SQL strings built with `format!` (identifier or column-list
interpolation next to bound parameters, not reviewed), 15 non-literal `Command::new`, 1 shell spawn; none in the
TypeScript rules. **Six files failed to parse** (`governance/computer/mod.rs`, `host/process.rs`,
`host/process/unix_tree.rs`, `crew/cancel.rs`, the fake engine's `acp.rs` and the desktop shell's `system.rs`).

The project's other scanner had 11 open alerts, all in test, tooling and script files (cleartext logging and
transmission, reflected XSS, incomplete sanitization) and 7 dismissed. The two sets do not overlap: the starter rules
do not target those classes and the scan excluded test files. This is a one-time snapshot, not the side-by-side run
[the CI gate](ci-gate.md) asks for.

## Not established

Linux and Windows builds; telemetry beyond "no network attempt in these runs"; whether the findings are real; the
release binary's behaviour; any live routing of the skill.
