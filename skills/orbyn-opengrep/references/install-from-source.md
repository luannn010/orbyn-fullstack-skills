# Install Opengrep from the pinned source

The library pins the engine in [source-pin.json](source-pin.json): release `v2.0.0`, commit
`526deafe6f0519c272bbee316fea8df26dd85dfa`, licence LGPL-2.1. The engine is copyleft, so its source stays
outside this repository: it is downloaded into the ignored `orbyn-references/` folder and built there. Nothing
from it is copied into the library.

## What the build needs

Read from the engine's own macOS release script and Makefile at the pin, and confirmed by a build:

- **OCaml 5.5.1** through `opam`, and `dune` installed into that switch (the opam file only requires 5.2.1 or later;
  the engine's INSTALL.md says 5.5.0, its release scripts say 5.5.1)
- **Homebrew packages on macOS:** `opam`, `pcre2`, `gmp`, `libev`, `coreutils`, `gettext`, `pkg-config` and **`bash` 5**
  (`make setup` refuses to run on macOS's own Bash 3.2)
- a C toolchain, `make` and `git`

## The sequence that worked (macOS, Apple Silicon, about 15 minutes)

Keep OCaml and every OCaml package out of the home folder by giving opam its own root under the ignored folder:

```sh
brew install opam pcre2 gmp libev coreutils gettext bash pkg-config
export OPAMROOT="$PWD/orbyn-references/opengrep-opam" OPAMYES=true
opam init --no-setup --bare
opam switch create 5.5.1          # compiles OCaml, a few minutes
eval "$(opam env --switch=5.5.1)"
opam install -y dune
export LIBRARY_PATH="$(brew --prefix)/lib"   # the engine's script sets this so lwt links libev
python3 skills/orbyn-opengrep/scripts/opengrep_source.py build --yes
```

If Homebrew cannot write its cache folder (it was root-owned on one machine), point `HOMEBREW_CACHE` and
`HOMEBREW_LOGS` at the ignored folder rather than changing ownership. On that run the opam root was about 1.1 GB and
the build tree about 3.0 GB.

## Linux: build in an Alpine container (verified in CI)

Do not build on Ubuntu 24.04: its `libpcre2-dev` is 10.42 and the engine needs 10.43 or newer (the link step fails with
`libpcre2 >= 10.43 is required`). The engine's own Linux release is built inside an Alpine container with static pcre2 and
gmp, and that is what worked:

- **Image:** `alpine:3.22`, pinned by digest (`sha256:49340b34…e898f` when this was written) so a moved tag cannot change the
  build.
- **Script:** [scripts/build_linux_in_alpine.sh](../scripts/build_linux_in_alpine.sh) runs inside the container with the
  pinned checkout mounted at `/workspace`: it installs the base packages and `opam`, then the engine's own library list with
  `make install-deps-ALPINE-for-semgrep-core`, builds the tree-sitter runtime, creates the OCaml 5.5.1 switch, installs
  `dune` and the opam dependencies, runs `make core` and writes `artifacts/opengrep` (a static binary that runs on Ubuntu).
- **Install the engine's libraries without `--no-cache`.** The engine's Makefile warns that `apk add --no-cache` hides
  `pkgconf` from opam and the dependency solve fails (opam issue 5186); a script that used it failed exactly that way.
- **Do not use the `setup-ocaml` action** for this build: it leaves no opam switch for `make setup` to find.
- **Time:** about 13 minutes on a hosted runner (OCaml and the opam packages compile from source), then a few seconds per
  scan. Cache the binary by the pinned commit.

Check out the commit first (`opengrep_source.py reference` downloads it, or clone and check out the exact commit with its
submodules), then:

```sh
docker run --rm --volume "$PWD/src:/workspace" --workdir /workspace --env OCAML_VERSION=5.5.1 \
  alpine:3.22@sha256:<digest> sh /workspace/build_linux_in_alpine.sh
```

(Copy the script next to the checkout first.) The app's advisory workflow does exactly this; it needs Docker, which was
not running on the maintainer's Mac, so the container recipe was verified on a hosted Linux runner, not locally.

## What the helper does

1. **`status`** lists the pin, whether a reference copy exists and which tools are missing, including an old Bash. It
   installs nothing.
2. **`reference`** (no code runs) downloads the pinned commit as an archive into
   `orbyn-references/opengrep/opengrep/<commit>/` with a `<commit>.json` receipt. It refuses unsafe archive paths,
   skips links, checks the commit id GitHub records in the archive against the pin when there is one, and refuses to
   write if `orbyn-references/` is not ignored by Git. An interrupted run leaves a folder with no receipt: the next
   run refuses and tells you to move it aside.
3. **`build --yes`** clones into `orbyn-references/opengrep-opengrep/build/<commit>/`, checks out the exact pinned
   commit (it stops if the checked-out commit differs), initialises the submodules, runs `make setup` and `make core`,
   and prints the path of `bin/opengrep`. `make setup` builds the tree-sitter library and installs the OCaml packages
   through `opam`, so this step runs upstream build scripts and needs `--yes`. The commit and the submodule commits are
   pinned; the opam packages are not, so a build trusts the network at that step. The helper refuses a references
   folder Git does not ignore and an existing build folder that is not a clean checkout, and it never deletes anything.
   A checkout with a nested `.git` is held, not removed, by the workspace cleanup.
4. **Verify the binary:** `bin/opengrep --version` (it printed `2.0.0`), then a one-line rule with an `ok` and a
   `ruleid` case under `opengrep test` ([rule writing](rule-writing.md#tests)). Record the version.

Do not install through an installer script, and do not install a toolchain as a side effect of a task: if tools are
missing, report which and stop, and get a yes for the Homebrew packages.

## Keeping the pin current

A newer release is a lead, not an update. Use the [upstream review](../../orbyn-upstream-review/SKILL.md) method:
resolve the full commit, read the licence at it, review the diff, and change the pin and `source-pin.json` in
one reviewed change. The pin file is the single place the commit is named.

## Limits

Built and run on macOS 27 (Apple Silicon) and, separately, on a hosted Ubuntu runner through the Alpine container above: see the [verification record](verification-2026-11-21.md). The helper's `build` is the macOS path and does not cover Linux (it stops on Ubuntu's old pcre2 at the link step).
A Windows source build is not covered here (the upstream project ships Windows binaries). The built binary
was not signed: the build's own strip step prints that it invalidates the code signature.
