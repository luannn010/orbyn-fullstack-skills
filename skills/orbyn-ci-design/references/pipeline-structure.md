# Pipeline structure for many services and environments

Use when one repository builds or deploys several services, or deploys to more than
one environment. Platform-neutral; GitHub Actions is the worked case.

## One manifest owns the routing

Keep one checked-in manifest that says, for each service: the paths that belong to it,
the checks it needs, and per environment its deploy target and whether a person must
approve. Rules shared by every service (build, unit tests, security scan) are written
once; per-service and per-environment rules live in the manifest, not in branches of a
script. Two entries never claim the same path for the same environment.

```json
{
  "schema_version": 1,
  "shared_paths": ["packages/shared/**"],
  "ignored_paths": ["docs/**", "*.md"],
  "services": {
    "api": {"paths": ["services/api/**"], "checks": ["unit", "contract"],
            "deploy": {"staging": {"target": "api-staging"},
                       "production": {"target": "api-prod", "approval": "required"}}},
    "web": {"paths": ["apps/web/**"], "checks": ["unit", "e2e"],
            "deploy": {"staging": {"target": "web-staging"},
                       "production": {"target": "web-prod", "approval": "required"}}}
  }
}
```

## A selector decides, the platform runs

1. A selector reads the manifest and the complete change set and prints the matrix:
   `ci_scope.py services --manifest services.json --base <sha> --head <sha> --event pull_request --environment production`
   ([`ci_scope.py`](../scripts/ci_scope.py)) prints `{"include": [...]}` with each
   affected service, its checks, its target and approval for that environment, and the
   reason it was picked; `--github-output` writes it for the next job. A shared path, a
   path no service owns, or incomplete evidence selects every service, as
   [change scope](change-scope.md#encode-a-conservative-fast-path) requires. Where the
   build system has its own [affected targets](affected-targets.md) query, use that.
2. The workflow fans out one job per matrix entry. Each job gets its own status, runs
   in parallel, retries alone and keeps its own record of what went where.
3. Each job calls small step scripts (build, migrate, deploy, smoke test) that also run
   on a laptop with the same arguments, so a failure can be reproduced without CI.

Do not run every deploy from one long orchestrator script: a failure halfway leaves a
partial deploy with no per-service record, nothing runs in parallel, and the
platform's approvals and environment secrets cannot apply to each step.

Share pipeline rules as reusable workflows or shared actions with inputs (service,
environment), one owner each, instead of copying job definitions.

## Environments are enforced by the platform

Give each environment its own secrets and protection rules in the CI platform:
production requires an approval and accepts deploys only from the protected branch.
A selector or script never grants that approval, and a pull request's code never runs
with deploy secrets. Promotion stays the deliberate decision in
[keep CD separate](change-scope.md#keep-cd-separate).

## Make it fast

Measure first: the slowest step, and how long a PR waits to turn green. Then:

- **PRs run one lane.** Run the runtime and platform production uses on PRs, and the
  full version and OS matrix on the main branch, nightly and before a release. Require
  only the PR lane, so a PR never waits for a lane that does not run on it.
- **Cheap checks first.** Format, lint, types and static checks run before the test
  suite, so a typo fails in seconds rather than after it.
- **Run only what the change affects** on a PR, and the full suite on the main branch
  and nightly.
- **Make slow tests cheaper before splitting them.** Build an expensive fixture once
  per class and copy it per test; fake a slow side effect (the system Trash, the
  network, a browser launch) and keep one real end-to-end test for it; inject a clock
  instead of sleeping. Then split the slowest module into parallel units and start
  the slowest first: the run is never shorter than its longest unit.
- **Size worker counts to the work:** subprocess-heavy tests wait on I/O and can use
  more workers than cores.
- **Cache dependencies** by lockfile hash, and build once and reuse the artifact
  downstream.
- **Cancel superseded runs** on the same branch, and stop a job early only when
  nothing after it is useful.
- **Keep a time budget.** Give the PR lane a target, such as five minutes. A run that
  goes over it is a defect: find and fix the slowest step instead of accepting drift.
  Report an overrun as a warning with the slowest jobs named. Do not make time a
  required check: runner speed varies by a minute or two, so it would fail PRs at
  random, and a failing job also turns the run red for every workflow that reacts to it.
- **Never retry a failure into green.** A rerun is only for a named infrastructure
  failure outside the code (a download or registry 5xx, a network timeout), after the
  run finishes, with the cause in the PR. A crash or timeout inside a real test is a
  flaky test, not infrastructure. A proven flaky test is quarantined, with an
  issue and an owner, so it neither blocks PRs nor hides real failures; fix it or
  delete it. An automatic rerun workflow is a retry policy too: limit it to named
  infrastructure jobs, record every rerun, and alert if the rerun fails as well, or the
  flake count stays invisible. See the [bulk method](bulk-failures.md) for many failures at once.
- **Going further:** sharding, required aggregates, cache warming, CI-only build
  profiles, job selection and merge watchers are in [making CI faster](ci-speed.md).
- **Use a merge queue** when several PRs land a day and main breaks from combinations
  that passed alone. It tests each PR on the latest main, so PRs need not re-run after
  every merge.

## Keep main green and visible

A PR lane that runs less than the main branch lets main go red without blocking anyone.
Nobody is waiting on that run, so nobody looks. In one project the browser suite stayed
red on main for 11 pushes, about 20 hours, because nothing said so.

- **Alert on a red main run.** A small workflow on the completed CI run, for the main
  branch only, opens one issue ("CI is red on main") with the run, the commit, the failed
  jobs and the merged PR. Further red runs add one comment each, keyed on the run id so a
  rerun event cannot duplicate it. A green run closes the issue. Ignore cancelled and
  skipped runs.
- **Keep it quiet.** Wait for a retry the pipeline will make itself instead of alerting
  on the first attempt. Do not let an older run that finished green close the issue while
  a newer run on main is red.
- **Treat the workflow as untrusted-input code.** It runs from the default branch and
  checks out only its own scripts. Commit and PR titles are data: pass them as
  environment or JSON, never into a shell string, and show them as inert code.
- **A lost event is possible** (a platform outage can drop the push event). A nightly
  run on main covers it.
- **A merge queue is the stronger fix, with a cost.** It runs the checks on every entry,
  so the full suite per merge is minutes the PR lane never paid (about 29 against about 6
  in one project). Decide it with the open-PR volume and the suite's flake rate in
  hand: a flaky shard blocks everyone.

## Fewer runs per PR

Every push is a full run, so the cheapest run is the one that never happens:

- Push one batch of fixes, not one commit per comment.
- Keep review rounds converging ([make review rounds converge](../../orbyn-workflow/references/engineering-scope.md#make-review-rounds-converge)).
- Let a standing user instruction cover a low-risk class of PR, such as docs-only PRs
  when every check is green ([merge only on the user's instruction](../../orbyn-workflow/playbooks/opening-a-pr.md#merge-only-on-the-users-instruction)).

A pre-push hook catches cheap failures before they cost a run. Instruction lines get
skipped by agents and people; a hook does not. Make it opt-in, mirror the cheap-checks job
exactly, run only the checks for the changed paths, never build or test, and print a
line when it skips a check it cannot run instead of passing silently.

Track time to green per PR, rounds per PR and the flaky-test rate, not only run
length. Waiting usually costs more than running.
