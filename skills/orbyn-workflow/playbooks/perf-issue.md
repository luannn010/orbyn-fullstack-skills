# Performance

The lead pins the workload and baseline, owns the interpretation and uses the
parent [workflow](../SKILL.md) for substantial diagnosis and implementation.
Write the throughput checkpoint, delegate bounded investigation of expensive
phases, then assign the supported optimization to an Engineer with owned files.
Children investigate or implement their own assigned slice directly.

Review the diff and perform authorized measurement of equivalent completed work.
Retain output quality, authority and coverage. Label cold/warm runs and unmeasured
costs. Smaller output alone does not prove lower tokens or faster execution.
Missing baseline or runtime access remains an evidence gap, not an assumed gain.

Before measuring, and before trusting, reporting or acting on a number, follow
[explain the number](../references/principles/explain-the-number.md): name the
limiter, check the arithmetic against it and rule out a wrong measurement.
Vet the baseline with it before this playbook plans from it.

Before a comparative claim, inspect what the harness actually times and counts.
Confirm the intended work completes inside that interval, validate its result and
count errors, rejected requests, retries and timeouts. Match relevant builds,
versions, data, concurrency and configuration across candidates; label deliberate
differences. Profile separately to identify the limiting resource without mixing
instrumentation overhead into the reported timing.

Repeat and alternate comparable runs when the claim needs it. Report units, the
chosen statistic, run count and variation; one observed run is a preliminary
measurement, and a difference within noise is inconclusive. Relate a helper's
speedup to its share of the user-visible path rather than claiming the whole flow
improved by that percentage. Preserve the harness, revision and raw outcomes so
another agent can assess the same claim.

## Sustained optimization

Use this loop only for requested sustained optimization, not every known defect.
Before expensive runs, state the decision-changing result, measured noise floor,
correctness/quality floors, workload, resource/time budget and stopping predicate.
Contrast known slower/faster, empty and erroneous work to establish harness
sensitivity. Freeze harness, input and baseline identities before candidate trials;
a harness change is a new experiment, not an implementation speedup.

Profile the limiter, then choose one falsifiable hypothesis. Prefer removing,
reusing, reducing or deferring unnecessary work before concurrency or micro-tuning.
Measure equivalent completed work and errors through the frozen interval, alternate
comparable trials and preserve every reject. Keep a candidate only when correctness
and decision thresholds pass; revert only its owned unsuccessful diff, preserving
unrelated work. Checkpoint accepted units only within delivery authority.

For an adoption comparison, tune each viable option to production-appropriate
settings or explain an untuned limiter. An as-shipped benchmark is legitimate
when labeled, but cannot silently become a universal winner. Check physical and
end-to-end plausibility: a phase consuming 10% of elapsed time cannot by elimination
alone save 50% of the same total. Do not invent hardware bandwidth. A zero-work
or error-fast path is not a gain. On plateau, use evidence to rank a different
mechanism or stop at the declared budget with an inconclusive/blocked result;
no arbitrary minimum iteration count, relaxed target or unlimited hillclimb.

For code that runs every frame or tick, read [real-time loops](../references/real-time-loops.md). For ordinary UI or RN motion, read the [motion performance method](../../orbyn-ui-design/references/animation-performance.md). Compare the same completed interaction under the same workload, preserving input/layout and runtime identity; screenshots alone cannot establish speed.

## Slow screen over a local or HTTP/1.1 service

Use when a screen feels slow but the service answers fast, or many calls take
seconds together. Measure the running system before reading code or building a mock.

1. **Time each call directly** from outside the app (for example `curl`), two
   rounds (cold, then warm), and read the service's own request trace (name,
   duration, end time).
2. **Compare server time with arrival time.** A call that takes 1-2 ms in the
   handler but arrives 0.3-2.4 s after its siblings is queueing before the handler.
   Use the client's request timing (DevTools *Queueing*/*Stalled*) or the server's
   accept time to tell client queueing from a full server worker pool.
3. **Count connections.** A browser or webview holds about 6 HTTP/1.1 connections
   per host and port, often shared across all the app's windows, and browsers need
   TLS for HTTP/2. List the server's established sockets, one side only (for
   example `lsof -a -p <server pid> -iTCP:<port> -sTCP:ESTABLISHED`), and name what
   holds each: event streams, slow reads, polls. Events carried over a WebSocket or
   the host's IPC do not use these connections.
4. **Fix both sides.** Server: [cache slow reads](../../orbyn-backend-design/references/slow-read-caching.md).
   Client: [lane the slow reads](../../orbyn-ui-design/references/async-state.md#keep-slow-reads-from-starving-the-screen).
   Each owner lists its traps.
5. **Re-measure the shipped build** from the app's own trace, the same way as
   steps 1-2. Cold first reads stay slow; keep them off the interactive path
   rather than claiming they got faster.

Two traps cross both sides: a poll queued behind slow reads shows state that is no
longer true, and capping slow reads can slow another screen that needs them, so
re-measure every screen that uses a laned call. Give an independent reviewer the
diff with the owners' check lists.

Example receipt (warm repeat visit, same machine, baseline build vs candidate
build; one run each, so preliminary): list read 1.8 s to 1 ms; settings read
0.44 s to 2 ms; spread of sibling arrival times 0.3-2.4 s to 6-160 ms. Cold reads
(3-7 s) unchanged, moved off the interactive path.

## Ticks that carry nothing

A timer that refetches every few seconds costs the same whether or not anything
changed, when the answer is written into state as fresh objects: every subscriber
below it sees new data. Ask what the tick did before optimizing the view. An
unchanged payload should cause no state write, no object identity change and no DOM
mutation. Fix the write rather than the render: compare the payload, keep the
objects that did not change, replace only the entries that did, and reserve
`loading` for a first read rather than every refresh.

Measure the tick, not the screen. Hold one poll interval unchanged and record script
time per tick at two or three data sizes, then count mutations inside the affected
subtree over a window where nothing should change. Zero is the target for an
unchanged tick. A nonzero count is either the poll or another clock, so name which:
an elapsed-time readout changing once a second looks exactly like a poll that
rebuilds rows, and optimizing the wrong one shows no gain.

Keep a changed payload working. A test that changes one field and waits for the view
to show it is as necessary as the identity test, because a cache that never updates
passes the second one alone.

## Build budgets are constraints, not latency results

Use for a changed startup/build/deployment boundary with an actual workload or
service constraint. Derive the budget from the consuming project's delivery,
parse/initialization or diagnostic needs; record its owner/source, artifact types,
units, compression basis, per-file versus aggregate scope and what blocks delivery.
Reuse its bundler/build check. The project sets its own number; do not import another product's byte limits or add
a plugin/benchmark framework solely to match this example. For the CI gate, see
[size budget](../../orbyn-ci-design/references/release-verification.md#fail-the-build-on-a-size-budget).

Synthetic lazy export viewer: an existing build gate limits the emitted entry's
static JS/CSS dependency closure to a project-agreed budget `B`. Count each asset
once; state whether dynamic viewer assets are excluded until used. A separate gate
requires maps for the chunks the diagnostic contract covers, with a map-size bound
`M`. Not every product requires maps, and private maps need not be publicly served.
Use the target's existing access/upload policy; no upload or credential access is
implied by a local build check.

| Selected control | What it should establish |
| --- | --- |
| Legal closure just under/at the declared inclusive `B` | Correct inclusion, byte units and comparator, not an indiscriminate build failure |
| One byte over `B`, including a shared static import | Gate fails with the owned asset/reason; renaming or splitting chunks cannot hide the same startup closure |
| Missing required map or one byte over `M` | Diagnostic-artifact gate fails; a deliberately exempt non-code asset remains legitimate |
| Deferred viewer opened by the user | Required work and errors are observed through readiness; a shell becoming visible is not the viewer finishing |

These are proposed fixture controls, not executed build or speed measurements.
For a file-oriented constraint use file controls instead; do not silently substitute
startup-closure size for a provider's per-artifact limit. Code splitting/lazy import
presence or smaller bytes alone do not establish fewer fetched bytes, lower memory
or faster startup. Measure those outcomes separately with actual network/runtime
and cold/warm identity. Retain an environment-skipped profile as skipped.

## Example measurement receipt

Keep the record in the existing task output, with raw outcomes rather than a new
mandatory tracker. For a local grouping microbenchmark, record:

- Exact baseline/candidate, build and harness/input hashes; runtime/browser,
  device/CPU and any emulation/throttle; cache/worker state and configuration.
- Interval: for example, transformation invocation through completed result;
  explicitly excluded network, worker/IPC, DOM/layout and presentation costs.
- Correctness witness: equivalent expected groups/values and error behavior,
  not only a checksum/count that could match incorrect output.
- Warmups/samples and chosen distribution/statistic with units, run order,
  failures/timeouts, raw output location and observed resource measures.
- Decision and limits: planned/not run remains unverified; a local phase change
  is not an end-to-end speedup or representative low-end device result.

Match the receipt to the claim. A draw call plus next frame is a paint opportunity,
not proof pixels were presented; one module request is a request-count observation,
not proof of compilation reuse. A finite no-repaint observation has that window,
not an indefinite guarantee. Identify the actual candidate/server when a harness
reuses one. Use the existing comparison loop above for equal completed work,
negative controls, alternating runs and uncertainty; no fixed sample count or
entire-app benchmark follows from this example.
