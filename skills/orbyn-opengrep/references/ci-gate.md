# Opengrep in CI, alone or beside CodeQL

Use when adding Opengrep to a pipeline or replacing another static-analysis scanner. Placement and
timing follow [orbyn-ci-design](../../orbyn-ci-design/SKILL.md); this page is only what is specific
to the scanner.

## Replace a scanner only after comparing them

A scanner swap nobody compared is a quiet gap, and the new tool can look green simply because its rules
see less. Before turning the old one off:

1. List the vulnerability classes the current scanner has reported in this project (closed alerts and
   the rule ids behind them) and name the Opengrep rules that cover each. Note the languages involved:
   the two tools do not support the same set, and interfile taint depth is a limit (`--interfile-depth`).
2. Run both on the same pull requests for a stretch you choose in advance (for example two weeks), and
   record every finding one reports and the other misses.
3. Count what the new scanner could not read. `--json` lists unparsed files under `errors`. In one trial the Rust
   parser rejected six of a project's files (`&raw const`, async closures), among them process-spawning and sandbox
   code: a clean result for them would mean nothing. Report every such file as uncovered.
4. Write down what the new scanner does not cover and who accepted that. Only then disable the old one.

A first trial showed why the comparison matters: the other scanner's open alerts were in test, tooling and script
files and were about cleartext logging, cleartext transmission, reflected XSS and incomplete sanitization, which
starter pattern rules for process spawning, SQL built with `format!` and TLS settings did not touch. Cover each
alert class with a taint rule and a test before retiring the old scanner.

## Placement

- **A separate job,** advisory first (not a required check), and required once it has been stable for a
  stretch. Required status names stay stable ([required checks](../../orbyn-ci-design/references/ci-speed.md#keep-a-required-check-stable)).
- **Fail on findings** with `--error` (exit 1). Write `--sarif -o results.sarif` when a code-scanning view
  is wanted; uploading SARIF needs a write permission to the security events and belongs in its own job.
- **On a pull request** use `--baseline-commit <base-sha>` so only new findings show. It needs the base
  commit in the checkout (fetch depth); outside a Git directory or with an unknown commit the scan aborts. On main
  and the nightly run, scan everything.
- **Time and memory count against the PR budget.** Measure the job, and use `--timeout`, `--max-memory`
  and `--interfile-timeout` rather than letting a rule run unbounded.

## Trust

- **Pin the binary:** the build from the pinned commit ([install from source](install-from-source.md)),
  cached by that commit, or a release asset checked against the checksum the project publishes for it (or against a build of the pinned commit you made yourself). Never fetch and run an installer
  inside a workflow. Pin actions to commits.
- **Write the rules yourself where you can.** The official community rules repository is a fork of Semgrep's rules under LGPL-2.1 with a Commons Clause that forbids selling, and its README says the rules are for research, testing and benchmarking. Do not copy them into this library. A local clone under the ignored `orbyn-references/` folder (`opengrep_source.py reference --slug opengrep/opengrep-rules`) can be pointed to with `--config <folder>`, but only after the maintainer has accepted that licence for the project. Rules written for the project's own risk list have no such question.
- **Pin and review the rules** in the repository like code, with tests. Do not fetch a ruleset at run
  time from a registry in a job that has secrets. A fork's pull request runs unprivileged and with no
  secrets, as with any other job.
- **Suppressions** (`nosemgrep`, `noopengrep`) carry a rule id and a reason. Count them in the report so a
  rising number is visible.

## What this does not establish

A passing job means the pinned rules found nothing in the paths and languages they cover. It is not a
security review, and it does not replace [orbyn-security-audit](../../orbyn-security-audit/SKILL.md).
