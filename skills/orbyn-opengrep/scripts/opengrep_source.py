#!/usr/bin/env python3
"""Fetch and build OpenGrep from the commit pinned in references/source-pin.json.

  reference   download the pinned source as a safe archive into the ignored
              orbyn-references/ folder, for reading (no code is run)
  build --yes check out the exact pinned commit with its submodules and run the documented
              make steps; this runs upstream build scripts, so it needs --yes
  status      show the pin, what is on disk and which build tools are missing

Nothing is installed globally and nothing is run from the source except under build --yes.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN_FILE = HERE.parent / "references" / "source-pin.json"
LIBRARY = HERE.parents[2]
MAX_BYTES = 800 * 1024 * 1024
MAX_FILES = 200_000
MAX_DOWNLOAD = 400 * 1024 * 1024
SLUG = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REVISION = re.compile(r"^[0-9a-f]{40}$")


class Refused(Exception):
    pass


def load_pin(slug, pin_file=PIN_FILE):
    if not SLUG.match(slug) or any(part in (".", "..") for part in slug.split("/")):
        raise Refused(f"not a valid source name: {slug!r}")
    for source in json.loads(Path(pin_file).read_text(encoding="utf-8"))["sources"]:
        if source["slug"] == slug:
            if not REVISION.match(source.get("revision", "")):
                raise Refused(f"the pinned revision for {slug} is not a full 40-hex commit")
            if not str(source.get("url", "")).startswith("https://"):
                raise Refused(f"the pinned url for {slug} is not https")
            return source
    raise Refused(f"no pin for {slug} in {pin_file}")


def ignored(root):
    """True when git ignores root, False when it does not, None outside a repository."""
    probe = str(Path(root) / "_ignore_probe" / "x")
    cwd = Path(root)
    while not cwd.is_dir() and cwd != cwd.parent:
        cwd = cwd.parent
    code = subprocess.run(["git", "check-ignore", "-q", probe], cwd=cwd).returncode
    return {0: True, 1: False}.get(code)


def extract(archive, dest, expect_commit=None):
    """Extract a GitHub tarball without its top folder; skip links, refuse unsafe names.

    GitHub records the commit id in the archive's pax header; when it is there it must equal expect_commit.
    """
    skipped, count, total, header, first = [], 0, 0, None, True
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar:
            if first:  # the global pax header is only available once the first member has been read
                header, first = (tar.pax_headers or {}).get("comment"), False
                if expect_commit and header and header.strip() != expect_commit:
                    raise Refused(f"the archive is for commit {header.strip()}, not the pinned {expect_commit}")
            parts = Path(member.name).parts
            if (member.name.startswith(("/", "\\")) or ".." in parts or Path(member.name).is_absolute()
                    or any(":" in part or "\\" in part for part in parts)):
                raise Refused(f"unsafe path in the archive: {member.name!r}")
            relative = Path(*parts[1:]) if len(parts) > 1 else None
            if relative is None:
                continue
            if member.issym() or member.islnk():
                skipped.append(str(relative))
                continue
            if not (member.isfile() or member.isdir()):
                skipped.append(str(relative))
                continue
            count += 1
            total += max(member.size, 0)
            if count > MAX_FILES or total > MAX_BYTES:
                raise Refused("the archive is larger than the allowed size")
            target = Path(dest) / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    return {"files": count, "bytes": total, "skipped_links": skipped, "commit_header_verified": bool(expect_commit and header)}


def download(url, opener=urllib.request.urlopen):
    with opener(url) as response:
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise Refused("the download is larger than the allowed size")
    return data


def reference(slug, root, pin_file=PIN_FILE, opener=urllib.request.urlopen, out=print):
    pin = load_pin(slug, pin_file)
    rev = pin["revision"]
    if ignored(root) is False:
        raise Refused(f"{root} is not ignored by git: add /orbyn-references/ to the ignore rules first")
    dest, receipt = Path(root) / slug / rev, Path(root) / slug / f"{rev}.json"
    if dest.exists() and receipt.is_file():
        out(f"already present: {dest}")
        return dest
    if dest.exists():
        raise Refused(f"{dest} exists without its receipt (an interrupted run?): move it aside and run again; nothing was changed")
    archive = download(f"https://codeload.github.com/{slug}/tar.gz/{rev}", opener)
    staging = Path(tempfile.mkdtemp(prefix="og-ref-"))
    try:
        info = extract(archive, staging, rev)
        dest.parent.mkdir(parents=True, exist_ok=True)
        pending = dest.parent / f".{rev}.json.tmp"
        pending.write_text(json.dumps({
            "repository": pin["url"], "revision": rev, "tag": pin.get("tag"), "license": pin["license"],
            "retrieved": datetime.date.today().isoformat(), "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "scope": "whole repository without submodules; links skipped", **info,
        }, indent=2) + "\n", encoding="utf-8")
        shutil.move(str(staging), str(dest))
        os.replace(pending, receipt)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    out(f"wrote {dest} ({info['files']} files, {len(info['skipped_links'])} links skipped, "
        f"commit header {'verified' if info['commit_header_verified'] else 'absent'}); receipt {receipt.name}")
    return dest


def bash_major():
    """The major version of the bash that make will find, or 0 when it cannot be read."""
    try:
        out = subprocess.run(["bash", "--version"], capture_output=True, text=True).stdout
    except OSError:
        return 0
    match = re.search(r"version (\d+)", out)
    return int(match.group(1)) if match else 0


def missing_tools(pin):
    names = [t for t in pin["build"]["tools"] if t != "cc"]
    gone = [t for t in names if shutil.which(t) is None]
    need = pin["build"].get("bash_min")
    if need and bash_major() < need:
        gone.append(f"bash>={need}")
    if shutil.which("cc") is None and shutil.which("gcc") is None and shutil.which("clang") is None:
        gone.append("cc")
    return gone


def build(slug, root, yes, pin_file=PIN_FILE, url=None, run=subprocess.run, out=print):
    pin = load_pin(slug, pin_file)
    if not yes:
        raise Refused("build runs the upstream build scripts (opam installs, make); rerun with --yes to allow it")
    if ignored(root) is False:
        raise Refused(f"{root} is not ignored by git: add /orbyn-references/ to the ignore rules first")
    gone = missing_tools(pin)
    if gone:
        raise Refused("missing build tools: " + ", ".join(gone) + f" (OCaml {pin['build']['ocaml']}, libraries: {', '.join(pin['build']['libraries'])}); nothing was installed")
    rev = pin["revision"]
    work = Path(root) / slug.replace("/", "-") / "build" / rev
    if work.exists():
        tracked = (work / ".git").exists()
        dirty = subprocess.run(["git", "-C", str(work), "status", "--porcelain"], capture_output=True, text=True).stdout.strip() if tracked else "x"
        if not tracked or dirty:
            raise Refused(f"{work} exists but is not a clean checkout; move it aside and run again")
    else:
        work.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--no-checkout", "--", url or pin["url"], str(work)], check=True)
    run(["git", "-C", str(work), "checkout", "--detach", rev], check=True)
    head = subprocess.run(["git", "-C", str(work), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if head != rev:
        raise Refused(f"checked out {head}, not the pinned {rev}")
    for step in pin["build"]["steps"]:
        out("+ " + " ".join(step))
        run(step, cwd=work, check=True)
    binary = work / pin["build"]["binary"]
    out(f"built {binary}; verify with: {binary} --version")
    return binary


def status(slug, root, pin_file=PIN_FILE, out=print):
    pin = load_pin(slug, pin_file)
    rev = pin["revision"]
    out(f"{slug} {pin.get('tag') or ''} {rev} ({pin['license']})")
    out(f"reference: {'present' if (Path(root) / slug / rev).is_dir() else 'absent'} under {root}")
    if "build" in pin:
        gone = missing_tools(pin)
        out("build tools: " + ("all found" if not gone else "missing " + ", ".join(gone)) + f"; needs OCaml {pin['build']['ocaml']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["reference", "build", "status"])
    parser.add_argument("--slug", default="opengrep/opengrep")
    parser.add_argument("--root", default=os.environ.get("ORBYN_REFERENCES", str(LIBRARY / "orbyn-references")))
    parser.add_argument("--pin-file", default=str(PIN_FILE))
    parser.add_argument("--yes", action="store_true", help="allow build to run the upstream build scripts")
    args = parser.parse_args(argv)
    try:
        if args.command == "reference":
            reference(args.slug, args.root, args.pin_file)
        elif args.command == "build":
            build(args.slug, args.root, args.yes, args.pin_file)
        else:
            status(args.slug, args.root, args.pin_file)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
