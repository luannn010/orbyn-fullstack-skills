# Prove a rewrite against the original

Use when a unit, service or whole app is rewritten, in another language or the same
one, and "done" means "behaves like before". The original's recorded behaviour is the
specification. A rewrite with no recording can only be argued about, never checked.

## Settle the equivalence bar first

Ask the user before recording, and write the answers into the task record:

- What counts as equal: exact bytes, or equal after named normalisation (key order,
  float formatting, whitespace, error text).
- Which edges are contract: exit codes, error messages, log lines, config and wire
  formats, flags, routes and status codes.
- For numeric code, the float tolerance the user picked. A tolerance covers floats
  only: integers and strings compare exactly, and so does the spelling of a number
  (`3` is not `3.0`).

## Record from the outside

- A CLI: arguments, stdin and environment in; stdout, stderr, exit code and written
  files out. A server: requests in; status, the headers that matter and bodies out. A
  library: calls to the public API with their results and errors.
- Record in an isolated environment: a sandbox database, fake credentials, no outbound
  effects. A recorded workload must never write to production.
- Take inputs from the existing tests, documented examples, real workloads and every
  deliberate failure (`throw`, `raise`, an error return). Add the semantic traps of the
  language pair from [language guidance](../../language-best-practices/SKILL.md), for
  example [porting into Rust](../../language-best-practices/references/rust.md#porting-into-rust).
- Find what varies by itself: run the original at least twice per case, changing the
  clock, random seed and hash seed between runs. Whatever differs is not behaviour to
  preserve: a timestamp or id, lines that arrive in another order, a stretch whose
  length changes. Mask it in the stored expectation; the rewrite's code stays
  untouched. Ask the user whether each ordering or length difference is contract,
  because those are the cases a rewrite can genuinely break.
- Before porting anything, replay the original against its own recording: it must
  pass every case.
- When the original has no tests, keep the recording: it is now its characterization
  suite.

## Move one unit at a time behind a front door

1. The new entry point owns the edge early and hands everything not yet ported to the
   original: re-run the old CLI with the same input, or proxy unported routes. It must
   replay every case before the first unit moves.
2. Count how many cases still reach the original. That number falls with each unit and
   never rises.
3. Port each unit close to the original's shape and error paths first. Refactor toward
   the new language's idioms in a later step, with replay green before and after.
4. Keep a per-unit switch back to the original until the last fallback is removed.
5. When replay goes red, rerun only the named case, change one thing, get it green,
   then rerun everything.

Units with no dependency on each other can go to children in parallel within the
resolved harness limits; the lead wires and replays them one at a time, and turns each
repeated mistake into a recorded rule or test.

## Rules that keep the proof honest

- When the rewrite and the recording disagree, fix the rewrite. A recorded case changes
  only with the user's approval and a written reason.
- A failing case is never fixed by loosening a tolerance or adding a mask.
- Every deliberate failure in the original is reached by at least one recorded
  failing case. A crash in the new code never matches a recorded error.
- Recordings cover only what they exercised. Report the inputs and edges they did not
  reach, next to the replay counts.
- Once nothing falls back, replay against the new build alone is the gate. Add it to CI
  only if the user wants that; from then on internals may diverge from the original's.

Report replay counts, how many cases still fall back, speed against the original where
speed was a goal, and every known behaviour difference. The user decides the cutover
and when the original is retired.

## Tools

Use the project's existing recording or snapshot tool first. A project that already
has [rust-anything](https://github.com/erkamyaman/rust-anything) installed for a
port to Rust can use its record, diff, replay and gate steps as this method's evidence.
Its `setup` command registers an MCP server in the user's agent configurations
([README](https://github.com/erkamyaman/rust-anything/blob/94a9f2d012c68cd1ad8067f21037357cdd6bcf5f/README.md)),
so installing it needs the user's approval like any other install.

## Source

Adapted from rust-anything by Erkam Yaman, MIT,
[`skills/rust-anything`](https://github.com/erkamyaman/rust-anything/tree/94a9f2d012c68cd1ad8067f21037357cdd6bcf5f/skills/rust-anything)
at `94a9f2d`, observed 18 November 2026; licence in
[`rust-anything-LICENSE.txt`](rust-anything-LICENSE.txt). Rewritten for any
language pair, with the tool optional.
