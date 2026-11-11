# Caching slow reads

Use when a read is slow (seconds) and its data may be a little old without harm,
and a measured screen depends on it. Measure first: see the
[slow screen method](../../orbyn-workflow/playbooks/perf-issue.md#slow-screen-over-a-local-or-http11-service).
Caching a read nobody measured adds a staleness bug for no gain.

## Stale while revalidate

Serve the last value at once, refresh in the background, then tell clients.

- **Single flight per key.** One refresh runs at a time. On a warm key later
  callers get the last value; on a cold miss they await the same in-flight load.
- **Bounded keys, named TTL constants and a hard staleness limit.** Past the limit,
  serve no stale value. Keep TTLs short until clients react to change events.
- **Key by everything that changes the answer:** account or tenant, resource scope,
  and any backend or option that changes the result.
- **Invalidate on every write** that changes the data, dropping exactly the
  affected keys. A background watcher must not drop a whole scope's cache on each
  pass.
- **Fence refreshes.** Tag each refresh with the key's generation; a write bumps
  it, and a refresh that finishes under an older generation is discarded. Callers
  waiting on a discarded load retry once under the new generation.
- **Failed refresh:** keep the last good value until the hard limit, then return
  the error; log the failure and retry later.
- **A force flag reads for real.** Refresh buttons and checks after an action use it.
- **Keep authorization and trust checks on cache hits.** A cached value is data,
  not permission.
- **Never cache progress or state that decides an action** (update progress, "is it
  running") behind a TTL.
- **Do not hold the cache map's lock, or any sync mutex, across the slow read.**
  Record an in-flight marker or shared future per key, release the lock, then await.
- **Announce fresh data** with a topic name per key family. Reuse the existing event
  stream if there is one.

## Check before merge

Staleness after each write path, key completeness, generation fencing, lock scope,
cold-miss behavior, and whether the first cold read still blocks an interactive
path. Cold reads stay slow; say so in the report.
