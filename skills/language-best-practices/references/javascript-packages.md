# JavaScript package managers, versions and reuse

Use for dependency preparation, toolchain pins or an explicitly authorized migration.
Workspace inspection alone installs nothing. Keep the project's existing package
manager unless the user authorizes changing it; npm remains supported.

## Resolve before installing

Read project instructions, `package.json` (`packageManager`, `engines`, scripts),
the owning lockfile, workspace configuration, runtime pin and CI setup. Confirm
the installed Node and package-manager versions in the selected worktree. A
`packageManager` pin and a conflicting lockfile or CI command need reconciliation,
not an arbitrary choice or a second lockfile. With no declared manager, use the
existing lockfile and documented commands; ask only if the evidence conflicts.

For authorized setup or migration, pin an exact tested package-manager version in
`packageManager`, select a compatible Node version through the project's existing
runtime mechanism, and use those versions in CI. Keep the supported Node range
distinct from its reproducible toolchain pin. Do not change global Node/PATH for
concurrent work. Toolchain pins, dependency versions and application release
versions are separate: a manager migration need not upgrade dependencies or bump
the app. Preserve the project's dependency range policy; align versions only when
compatible, never by forcing unrelated projects onto one graph.

## Reuse the matching installation

Check manifests, lockfile, manager version, Node/native compatibility, platform,
architecture, workspace links and install settings before reusing an installation.
A present `node_modules` directory alone is insufficient. Reuse a valid existing
installation; synchronize when inputs differ or evidence is missing. Follow a
required clean verification gate even when a warm installation is available.

| Project | Reproducible preparation when needed | Run a configured check |
| --- | --- | --- |
| npm with a committed lockfile | `npm ci` (recreates the installation) | `npm run check` |
| pnpm with a committed lockfile | `pnpm install --frozen-lockfile --prefer-offline` | `pnpm run check` |

Use only scripts the project defines. pnpm's `--prefer-offline` permits fetching
missing data; `--offline` fails if required store contents are absent. Do not
routinely delete installations, use `--force`, regenerate lockfiles or prune stores
to prepare an ordinary task. First-time migration may need downloads and linking;
an npm installation is not automatically a populated pnpm store.

## Optional pnpm migration

1. Preserve the current checkout and lockfile. Declare actual workspace members
   before importing a workspace; independent repositories need no combined workspace.
2. Select and pin a compatible pnpm version. Import the npm lockfile with
   `pnpm import`, review the resolved versions and peer differences, and separate
   intentional upgrades from migration fixes. Import is not proof of identical resolution.
3. Let pnpm prepare each worktree's own dependency layout using its shared content
   store. Inspect `pnpm store path` from that checkout; keep persistent stores
   outside disposable worktrees and on the same filesystem for hard-link reuse.
   Do not share another checkout's mutable `node_modules` or use one project's
   `virtualStoreDir` for independent graphs. Shared-store pruning is separate maintenance.
4. Update the project's commands, CI caches, dependency automation and change
   selectors for `pnpm-lock.yaml`, manifests and workspace/install configuration.
   Keep one authoritative lockfile per installation root after verification.
   Check required dependency build-script approvals for the pinned pnpm version.
5. Verify checks/builds and a second warm frozen install; where useful, prepare a
   disposable fresh worktree offline to prove store reuse. Report downloads,
   linking, dependency builds and application builds separately. Keep rollback
   instructions and report platform checks that were not run.

Cache the pnpm store separately from application outputs. CI cache namespaces must
respect OS/architecture, compatible Node/native ABI, pnpm/store version and install
settings; lockfile keys with compatible restore prefixes can reuse older package
contents. A cache hit still requires a matching frozen installation. Docker uses
its own layers or BuildKit store cache, not links into the host installation.

pnpm can reuse eligible dependency install-hook outputs through its side-effects
cache; inspect the pinned version and package behavior before relying on it.
Application build reuse needs the existing build tool's cache or artifacts keyed
by source, lockfile, toolchain, configuration and relevant environment inputs.
Build once and promote that same verified artifact. Do not add a remote cache,
global virtual store or task runner solely because pnpm is selected.

## Worked decisions

- An npm app needs a source fix: retain its npm lockfile and commands; run the
  matching existing installation without a manager migration or routine `npm ci`.
- Two pnpm worktrees have different lockfiles: install each frozen graph from the
  persistent store; reuse package contents without changing the other checkout.
- A previous revision's compiled output exists, but its build inputs are unknown:
  reuse eligible dependencies and rebuild the output instead of claiming a cache hit.

## Primary references

Reviewed 22 November 2026 for pnpm 10.x: [install options](https://pnpm.io/10.x/cli/install),
[lockfile import](https://pnpm.io/10.x/cli/import), [store, version and build settings](https://pnpm.io/10.x/settings).
Inspect the selected version's documentation before using newer optional features.
