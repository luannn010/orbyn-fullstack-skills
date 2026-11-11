# Making CI faster

Use when a pipeline is slow and the [make it fast](pipeline-structure.md#make-it-fast)
basics are in place. Each rule came from a measured run; measure yours the same
way before and after.

## Measure where the time goes

List each job's steps and times from the run itself, cold and warm (for GitHub,
`gh api --paginate repos/<owner>/<repo>/actions/runs/<id>/attempts/<n>/jobs`).
Report the required check's wall time, the PR's time to green and the main
branch's time separately, and what each change costs, such as runner minutes added
to PRs that used to skip a platform.

The time is often not where you guess. In one project a Windows test job was slow
because its runner starts a process per test, and process creation is expensive on
Windows; compiling was not the limiter.

## Shard the tests

- **Build once:** one job builds the binaries or service and uploads an artifact
  with short retention; every shard downloads it rather than compiling. For Rust,
  `cargo nextest archive` with `--archive-file` does this for the test binaries.
- **Balance by recorded duration** where you can: greedy longest-first over a
  checked-in durations file, refreshed from a timing report each shard uploads. A
  runner's count- or hash-based partition (for example nextest
  `--partition count:N/M`) is fine when the shards come out balanced.
- **Fail a shard that receives no tests,** and after sharding confirm the summed
  test count across shards equals the old single job's count.
- **Run once-only work on one shard.** nextest does not run doc tests; run
  `cargo test --doc` on one shard.
- **Stop adding shards** when fixed setup (checkout, toolchain, download) is bigger
  than the tests a shard runs. Measure your setup; in one project it was 1-1.5 min.
- **A flaky shard** follows the [rerun rule](pipeline-structure.md#make-it-fast):
  quarantine the test with an issue and an owner, never re-run into green.

## Keep a required check stable

Put a sharded or conditional required check behind one aggregate job with the exact
required name (the job's `name:`; through a reusable workflow it becomes
`caller / callee`). Follow the [always-triggered gate](change-scope.md#encode-a-conservative-fast-path):

- It runs with `if: always()`. Do not use `!cancelled()` or `success() || failure()`:
  on a cancelled run the aggregate is skipped, and GitHub treats a skipped required
  job as passing.
- It passes on `success`, and on `skipped` only for jobs the selector did not pick. It
  fails on `failure`, `cancelled` or any other skip. A test like
  `contains(needs.*.result, 'failure')` misses cancelled and skipped jobs.

Splitting a job can make the required check slower: each new job adds queue and
setup time on the critical path. Compare the required check's wall time before and
after, not just the work per job, and drop the split if the critical path got longer.

## Caches and build settings

- **Warm every new cache key on the default branch.** PRs can read their own,
  their base branch's and the default branch's caches, but not each other's. A new
  key or profile is cold on every PR until a main-branch job builds it. Use a key
  that does not embed the job id (for example rust-cache `shared-key`). Without a
  warm job, one project's first PR run went from 8 to 13 min.
- **Test-only settings get their own key.** In Cargo, flags that change only for
  test jobs (`RUSTFLAGS` such as a different linker, or the profile's debug level) change the
  build fingerprint and would thrash a shared cache. Each key adds pressure on the
  repository's cache quota (10 GB on GitHub), so watch for evictions.
- **A CI-only build profile** may trade runtime speed for build time on PRs, for
  example inheriting release with link-time optimisation off. In Cargo,
  `lto = false` still does thin local LTO unless `codegen-units = 1` or
  `opt-level = 0`; `"off"` disables it. Raise codegen units back to the default of
  16 if release lowered them. Main, nightly and release keep the real profile. Name
  what the PR build no longer covers, such as the production linker.
- **Cache downloaded build tools** (installers, bundler helpers), keyed on the
  tool's version. This also removes a flaky download from the path.

## Job selection

Select jobs from the [manifest](pipeline-structure.md#one-manifest-owns-the-routing),
not top-level workflow path filters, and let a path no job owns select every job.
A test in one job that reads another job's sources breaks when that job is not
selected: add those paths to its selection or remove the dependency.

## Merging on green

Prefer native auto-merge (`gh pr merge --auto`) or a merge queue: both wait for
every required check, including one still marked expected. A script that polls
`gh pr checks --required` can merge too early, because a required check that has
not reported yet (for example from a workflow that has not started) is not in that
list. If you must script it, wait for every workflow run on the head commit, not
one run.
