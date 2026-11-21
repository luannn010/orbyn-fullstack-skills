#!/bin/sh
# Builds the pinned Opengrep source inside an Alpine container, the way the engine's own Linux release is built: static
# pcre2 and gmp, and a libpcre2 newer than Ubuntu 24.04 ships (the engine needs >= 10.43). Our own steps; the commit,
# OCaml version and make targets come from the engine's pinned source. Run by .github/workflows/opengrep.yml with the
# pinned checkout mounted at /workspace; it writes /workspace/artifacts/opengrep.
set -eux

OCAML_VERSION="${OCAML_VERSION:-5.5.1}"
export OPAMROOT=/workspace/_opam
export OPAMCONFIRMLEVEL=unsafe-yes

apk add --no-cache git build-base zip bash libffi-dev zstd-static tar zstd curl opam
opam --version

git config --global --add safe.directory /workspace
cd /workspace

# The engine's own list of static libraries. Its Makefile installs them with plain `apk add` and says not to use --no-cache:
# otherwise opam does not see pkgconf as installed (opam issue 5186) and the dependency solve fails.
make install-deps-ALPINE-for-semgrep-core

# The tree-sitter runtime the engine links.
( cd libs/ocaml-tree-sitter-core && ./configure && ./scripts/install-tree-sitter-lib )

opam init --yes --disable-sandboxing --root="$OPAMROOT" --compiler="$OCAML_VERSION"
eval "$(opam env --root="$OPAMROOT")"
opam install -y dune
make install-opam-deps
opam exec -- make core

mkdir -p artifacts
cp -L bin/opengrep artifacts/opengrep
./artifacts/opengrep --version
