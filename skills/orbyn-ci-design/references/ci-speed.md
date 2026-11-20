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

Over 30 or more recent runs, split each job into waiting (created to started), setup
and running, at the median and at the 95th percentile, and fix the biggest bucket
first. In one project waiting was about zero and the test run and its compile were the
whole bill, so faster runners would have bought nothing.

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
- **Let PRs read caches but not save them.** Save only from the default branch
  (for Actions, `save-if` on the main ref). A PR cache is read only by that PR, and
  each copy of a large build cache counts against the quota. In one project 3.7 GB of
  PR copies pushed the repository over its 10 GB limit and put the main-branch caches
  at risk of eviction.
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

## Self-hosted runners

Moving jobs to your own machine adds capacity, and speed only when it is measured.
Run the job alone on a throwaway branch first, with nothing else local, and compare it
with the hosted run. In one project a local runner ran the tests 27% faster (100 s
against 138 s) but found no cache (probably because the cache key includes the
runner's OS; not confirmed), so the compile took 2 minutes longer and the job lost overall. With two runners on one
machine and both busy, the job took 648 s and a UI suite failed on timeouts.

- **Check what is shared.** Two runners on one machine share cores, memory and, often,
  the workspace, cargo home and package caches. Count machines, not runners.
- **Gate it on a variable** and say in the workflow that a job with no available local
  runner waits in the queue; it does not fall back to hosted. Unset the variable when the
  machine is down. Keep fork and bot runs on hosted runners.
- **Expect a persistent disk to mask failures.** A kept build or install folder can hide
  a clean-build failure; wipe or key it deliberately.
- **Start a new run to test a variable.** In one project a run created seconds before the
  variable was set stayed on hosted runners, so it proved nothing.

## Job selection

Select jobs from the [manifest](pipeline-structure.md#one-manifest-owns-the-routing),
not top-level workflow path filters, and let a path no job owns select every job.
A test in one job that reads another job's sources breaks when that job is not
selected: add those paths to its selection or remove the dependency. Prove the selector
with a planted change: alter a file only one job reads, hide the change from the selector
on purpose, and confirm the run goes red. A selector that is never shown to miss a change
is only assumed to work.

## Merging on green

Prefer native auto-merge (`gh pr merge --auto`) or a merge queue: both wait for
every required check, including one still marked expected. A script that polls
`gh pr checks --required` can merge too early, because a required check that has
not reported yet (for example from a workflow that has not started) is not in that
list. If you must script it, wait for every workflow run on the head commit, not
one run.
