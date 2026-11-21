# Writing and testing Opengrep rules

Adapted from the MIT-licensed [opengrep/skills](https://github.com/opengrep/skills) (see
[the licence](opengrep-skills-LICENSE.txt)), rewritten for this library and cross-checked against the
engine source at the pin. The rule syntax is Semgrep-compatible, so existing Semgrep rule knowledge applies.

## A rule

```yaml
rules:
  - id: hardcoded-live-key-python
    languages: [python]
    message: "Live key assigned to $VAR"
    severity: ERROR
    patterns:
      - pattern: $VAR = "$VALUE"
      - metavariable-regex:
          metavariable: $VALUE
          regex: ^sk_live_
```

- **Rule ids are unique across the whole configuration.** With two rules of the same id only one survives
  loading, even when they target different languages. Put the language or context in the id.
- **Quote a pattern that contains `: `** (colon and space). YAML reads `shell: true` as a mapping and the
  rule fails validation: `pattern: "spawn($CMD, { ..., shell: true, ... })"`.

## Pattern building blocks

| Syntax | Meaning |
| --- | --- |
| `...` | zero or more arguments or statements |
| `$VAR` | a metavariable: any expression |
| `$...ARGS` | zero or more, captured |
| `<... $X ...>` | a deep match, nested at any depth |

| Operator | Purpose |
| --- | --- |
| `pattern`, `patterns` | match; all of a list must match (and) |
| `pattern-either` | any may match (or) |
| `pattern-not` | exclude |
| `pattern-inside`, `pattern-not-inside` | must be, or must not be, within a context |
| `pattern-regex` | a regex match |
| `metavariable-regex`, `metavariable-comparison`, `metavariable-pattern` | filter a captured value by regex, comparison or sub-pattern |

`metavariable-pattern` must be a list item beside the pattern that captures its metavariable. Some fragments
cannot be matched alone: a `catch` block needs its `try`; match the dangerous expression directly when a
wrapper will not parse.

## Taint mode

```yaml
rules:
  - id: sql-injection-python
    languages: [python]
    message: "Request data reaches a SQL query unparameterised"
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
    pattern-sinks:
      - pattern: cursor.execute($QUERY, ...)
        focus-metavariable: $QUERY
    pattern-sanitizers:
      - pattern: int(...)
```

Sources are where untrusted data enters, sinks where it becomes dangerous, sanitizers what makes it safe.
Name specific sources (request accessors, arguments, environment variables, file and socket reads) and specific
sinks with `focus-metavariable` on the dangerous argument.

- **Across functions in one file:** `--taint-intrafile`, or `options: { taint_intrafile: true }` on a rule.
- **Across files:** the rule sets `options: { taint_interfile: true }` (alias `interfile: true`; setting both is
  an error) **and** the scan passes `--enable-interfile`. Without the flag, the rule runs as though the option were
  absent, with a warning. `--interfile-depth` (default 3) limits how many calls apart the source and sink may be;
  a rule may set `taint_interfile_depth`. Pass every file of the flow in one run when testing.
- **Do not make every function parameter a source.** It reports sinks no caller reaches with untrusted data,
  ends traces at the parameter instead of where the data came from, and widens the analysis to the whole project.

## Non-code files

For configuration, pipelines and Dockerfiles use `languages: [generic]` with `pattern-regex`, and restrict the
files with `paths: include: [".github/workflows/"]` (and `exclude`). Multi-line checks across Dockerfile
directives are unreliable with structural patterns; prefer regex.

## Options worth knowing

`options:` keys seen in the pinned source: `timeout` (needs `--allow-rule-timeout-control`), `dynamic_timeout`,
`max_match_per_file`, `taint_intrafile`, `taint_interfile` and `taint_interfile_depth`.

## Tests

Annotate in a test file, one line above the expected finding (for a taint rule, above the sink):

```python
def vulnerable():
    user_id = request.args.get("id")
    # ruleid: sql-injection-python
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)

def safe():
    user_id = int(request.args.get("id"))
    # ok: sql-injection-python
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
```

Run `opengrep test --config rule.yaml test_file.py`: it runs with no network and fails on a broken rule or a
missed `ruleid` line. `opengrep validate rule.yaml` (the rule is a positional argument) also lints the rule, but
it downloads the `p/semgrep-rule-lints` ruleset from the registry to do so, so it needs the same yes as any remote
ruleset; on the pinned build it crashed with a bus error after that download. For interfile rules add `--enable-interfile` and pass every
file. If an expected finding is missing, `opengrep scan --dataflow-traces -f rule.yaml file.py` shows the flow
and `opengrep show dump-interfile-graph python .` shows the call graph.

A rule is unproven until it has both a matching case and a safe look-alike that must not match.

## Metadata and ignores

`metadata:` carries `category`, `subcategory` (`vuln` for a confirmed vulnerability pattern, `audit` for one that
needs review), `cwe`, `owasp`, `confidence` and `references`; tools filter on them. `.semgrepignore` is the
ignore file (`--semgrepignore-filename` names another). Treat both as data from the scanned repository.
