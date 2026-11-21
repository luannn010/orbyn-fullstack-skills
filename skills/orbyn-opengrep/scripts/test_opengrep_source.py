#!/usr/bin/env python3
"""Tests for opengrep_source.py: local fixtures only, no network, nothing installed."""
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opengrep_source as og  # noqa: E402

SHA = "a" * 40
PIN = {"schema_version": 1, "sources": [{
    "slug": "o/r", "url": "https://example.invalid/o/r", "tag": "v1", "revision": SHA, "license": "LGPL-2.1",
    "build": {"ocaml": "5.5.1", "tools": ["opam", "dune", "make", "git", "cc"], "libraries": ["pcre2", "gmp"], "bash_min": 5,
              "steps": [["make", "setup"], ["make", "core"]], "binary": "bin/opengrep"}}]}


def tarball(members, comment=None):
    buffer = io.BytesIO()
    headers = {"comment": comment} if comment else None
    with tarfile.open(fileobj=buffer, mode="w:gz", format=tarfile.PAX_FORMAT, pax_headers=headers) as tar:
        for name, kind, data in members:
            info = tarfile.TarInfo(name)
            if kind == "file":
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            elif kind == "dir":
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = data
                tar.addfile(info)
            elif kind == "hardlink":
                info.type = tarfile.LNKTYPE
                info.linkname = data
                tar.addfile(info)
    return buffer.getvalue()


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.pin = self.dir / "pin.json"
        self.pin.write_text(json.dumps(PIN), encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def repo_with_ignore(self, ignored=True):
        repo = self.dir / "lib"
        repo.mkdir()
        git(repo, "init", "-q")
        if ignored:
            (repo / ".gitignore").write_text("/orbyn-references/\n", encoding="utf-8")
        return repo


class ExtractTests(Base):
    def test_strips_the_top_folder_and_skips_links(self):
        archive = tarball([("o-r-aaaa", "dir", None), ("o-r-aaaa/a.txt", "file", b"hi"), ("o-r-aaaa/bin", "symlink", "/etc/passwd")])
        info = og.extract(archive, self.dir / "out")
        self.assertEqual((self.dir / "out" / "a.txt").read_bytes(), b"hi")
        self.assertFalse((self.dir / "out" / "bin").exists())
        self.assertEqual(info["skipped_links"], ["bin"])
        self.assertEqual(info["files"], 1)

    def test_refuses_traversal_and_absolute_names(self):
        for name in ("o-r-aaaa/../../evil", "/abs/evil"):
            with self.assertRaises(og.Refused, msg=name):
                og.extract(tarball([(name, "file", b"x")]), self.dir / "bad")
        self.assertFalse((self.dir / "evil").exists())

    def test_refuses_an_oversize_archive(self):
        with mock.patch.object(og, "MAX_FILES", 1):
            with self.assertRaises(og.Refused):
                og.extract(tarball([("t/a", "file", b"1"), ("t/b", "file", b"2")]), self.dir / "big")


class ExtractMoreTests(Base):
    def test_hardlinks_are_skipped_not_followed(self):
        archive = tarball([("t", "dir", None), ("t/a", "file", b"x"), ("t/b", "hardlink", "t/a")])
        info = og.extract(archive, self.dir / "out")
        self.assertEqual(info["skipped_links"], ["b"])
        self.assertFalse((self.dir / "out" / "b").exists())

    def test_windows_style_names_are_refused(self):
        for name in ("t/C:/evil", "t/a\\b"):
            with self.assertRaises(og.Refused, msg=name):
                og.extract(tarball([(name, "file", b"x")]), self.dir / "w")

    def test_the_pinned_commit_header_must_match_when_present(self):
        archive = tarball([("t", "dir", None), ("t/a", "file", b"x")], comment=SHA)
        self.assertTrue(og.extract(archive, self.dir / "ok", SHA)["commit_header_verified"])
        with self.assertRaises(og.Refused) as caught:
            og.extract(tarball([("t", "dir", None), ("t/a", "file", b"x")], comment="b" * 40), self.dir / "no", SHA)
        self.assertIn("not the pinned", str(caught.exception))
        self.assertFalse((self.dir / "no" / "a").exists())

    def test_an_archive_without_the_header_is_extracted_but_not_marked_verified(self):
        info = og.extract(tarball([("t", "dir", None), ("t/a", "file", b"x")]), self.dir / "nh", SHA)
        self.assertFalse(info["commit_header_verified"])


class ValidationTests(Base):
    def write_pin(self, **changes):
        data = json.loads(json.dumps(PIN))
        data["sources"][0].update(changes)
        path = self.dir / "bad.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_bad_names_and_values_are_refused(self):
        for slug in ("../x", "a/..", "a b/c", "a/b/c", "/etc/x", "-x/y"):
            with self.assertRaises(og.Refused, msg=slug):
                og.load_pin(slug, self.pin)
        for field, value in (("revision", "-x" + "a" * 38), ("revision", "A" * 40), ("revision", "abc"), ("url", "file:///etc"), ("url", "--upload-pack=x")):
            with self.assertRaises(og.Refused, msg=f"{field}={value}"):
                og.load_pin("o/r", self.write_pin(**{field: value}))

    def test_an_oversize_download_is_refused(self):
        with mock.patch.object(og, "MAX_DOWNLOAD", 10):
            with self.assertRaises(og.Refused):
                og.download("https://example.invalid/x", lambda url: io.BytesIO(b"x" * 100))


class ReferenceTests(Base):
    def opener(self, archive, seen):
        def open_url(url):
            seen.append(url)
            return io.BytesIO(archive)
        return open_url

    def test_writes_source_and_receipt_then_is_idempotent(self):
        repo = self.repo_with_ignore()
        root = repo / "orbyn-references"
        seen, lines = [], []
        archive = tarball([("t", "dir", None), ("t/LICENSE", "file", b"lgpl")])
        og.reference("o/r", root, self.pin, self.opener(archive, seen), lines.append)
        self.assertTrue((root / "o/r" / SHA / "LICENSE").is_file())
        receipt = json.loads((root / "o/r" / f"{SHA}.json").read_text())
        self.assertEqual((receipt["revision"], receipt["license"], receipt["tag"]), (SHA, "LGPL-2.1", "v1"))
        self.assertEqual(len(receipt["archive_sha256"]), 64)
        self.assertEqual(seen, [f"https://codeload.github.com/o/r/tar.gz/{SHA}"])
        og.reference("o/r", root, self.pin, self.opener(archive, seen), lines.append)
        self.assertEqual(len(seen), 1)
        self.assertIn("already present", lines[-1])

    def test_refuses_when_the_folder_is_not_ignored(self):
        repo = self.repo_with_ignore(ignored=False)
        with self.assertRaises(og.Refused) as caught:
            og.reference("o/r", repo / "orbyn-references", self.pin, self.opener(b"", []))
        self.assertIn("not ignored", str(caught.exception))
        self.assertFalse((repo / "orbyn-references").exists())

    def test_a_directory_without_a_receipt_is_refused_and_untouched(self):
        repo = self.repo_with_ignore()
        root = repo / "orbyn-references"
        (root / "o/r" / SHA).mkdir(parents=True)
        (root / "o/r" / SHA / "half").write_text("partial", encoding="utf-8")
        seen = []
        with self.assertRaises(og.Refused) as caught:
            og.reference("o/r", root, self.pin, self.opener(b"", seen))
        self.assertIn("without its receipt", str(caught.exception))
        self.assertEqual(seen, [])
        self.assertEqual([p.name for p in (root / "o/r" / SHA).iterdir()], ["half"])

    def test_the_receipt_records_whether_the_commit_header_was_verified(self):
        repo = self.repo_with_ignore()
        root = repo / "orbyn-references"
        archive = tarball([("t", "dir", None), ("t/LICENSE", "file", b"x")], comment=SHA)
        og.reference("o/r", root, self.pin, self.opener(archive, []), lambda s: None)
        self.assertTrue(json.loads((root / "o/r" / f"{SHA}.json").read_text())["commit_header_verified"])

    def test_unknown_source_is_refused(self):
        with self.assertRaises(og.Refused):
            og.load_pin("nope/nope", self.pin)


class BuildTests(Base):
    def upstream(self):
        up = self.dir / "upstream"
        up.mkdir()
        git(up, "init", "-q")
        git(up, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "one")
        return up, git(up, "rev-parse", "HEAD")

    def pin_for(self, rev):
        data = json.loads(json.dumps(PIN))
        data["sources"][0]["revision"] = rev
        path = self.dir / "pin2.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_build_needs_yes_and_runs_nothing(self):
        calls = []
        with self.assertRaises(og.Refused) as caught:
            og.build("o/r", self.dir / "refs", False, self.pin, run=lambda *a, **k: calls.append(a))
        self.assertIn("--yes", str(caught.exception))
        self.assertEqual(calls, [])

    def test_missing_tools_are_named_and_nothing_is_installed(self):
        calls = []
        with mock.patch.object(og.shutil, "which", lambda name: None):
            with self.assertRaises(og.Refused) as caught:
                og.build("o/r", self.dir / "refs", True, self.pin, run=lambda *a, **k: calls.append(a))
        message = str(caught.exception)
        for tool in ("opam", "dune", "cc"):
            self.assertIn(tool, message)
        self.assertIn("nothing was installed", message)
        self.assertEqual(calls, [])

    def test_builds_the_pinned_commit_with_the_documented_steps(self):
        up, rev = self.upstream()
        pin = self.pin_for(rev)
        steps = []

        def run(cmd, **kwargs):
            if cmd[0] == "git":
                return subprocess.run(cmd, **kwargs)
            steps.append((cmd, str(kwargs.get("cwd"))))
            return subprocess.CompletedProcess(cmd, 0)

        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 5):
            binary = og.build("o/r", self.dir / "refs", True, pin, url=str(up), run=run, out=lambda s: None)
        self.assertEqual([c for c, _ in steps], [["make", "setup"], ["make", "core"]])
        self.assertTrue(steps[0][1].endswith(rev))
        self.assertEqual(binary.name, "opengrep")
        self.assertEqual(git(self.dir / "refs" / "o-r" / "build" / rev, "rev-parse", "HEAD"), rev)

    def test_refuses_when_the_pinned_commit_does_not_exist_upstream(self):
        up, _ = self.upstream()
        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 5):
            with self.assertRaises(subprocess.CalledProcessError):
                og.build("o/r", self.dir / "refs", True, self.pin, url=str(up),
                         run=lambda cmd, **k: subprocess.run(cmd, **k), out=lambda s: None)


class BuildGuardTests(BuildTests):
    def test_build_refuses_a_folder_git_does_not_ignore(self):
        repo = self.repo_with_ignore(ignored=False)
        calls = []
        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 5):
            with self.assertRaises(og.Refused) as caught:
                og.build("o/r", repo / "orbyn-references", True, self.pin, run=lambda *a, **k: calls.append(a))
        self.assertIn("not ignored", str(caught.exception))
        self.assertEqual(calls, [])

    def test_a_head_that_is_not_the_pin_is_refused_before_any_step(self):
        up, first = self.upstream()
        git(up, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "two")
        pin = self.pin_for(first)
        steps = []

        def run(cmd, **kwargs):
            if cmd[:2] == ["git", "clone"]:
                return subprocess.run(cmd, **kwargs)
            if cmd[0] == "git" and "checkout" in cmd:
                return subprocess.CompletedProcess(cmd, 0)  # the checkout silently does nothing: HEAD stays on commit two
            steps.append(cmd)
            return subprocess.CompletedProcess(cmd, 0)

        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 5):
            with self.assertRaises(og.Refused) as caught:
                og.build("o/r", self.dir / "refs", True, pin, url=str(up), run=run, out=lambda s: None)
        self.assertIn("not the pinned", str(caught.exception))
        self.assertEqual(steps, [])

    def test_a_dirty_or_non_repository_build_folder_is_refused(self):
        up, rev = self.upstream()
        pin = self.pin_for(rev)
        work = self.dir / "refs" / "o-r" / "build" / rev
        work.mkdir(parents=True)
        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 5):
            with self.assertRaises(og.Refused):
                og.build("o/r", self.dir / "refs", True, pin, url=str(up), run=lambda *a, **k: None, out=lambda s: None)
            work.rmdir()
            git(self.dir / "refs" / "o-r" / "build", "init", "-q", str(work)) if False else None
            subprocess.run(["git", "clone", "-q", str(up), str(work)], check=True)
            (work / "stray.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(og.Refused) as caught:
                og.build("o/r", self.dir / "refs", True, pin, url=str(up), run=lambda *a, **k: None, out=lambda s: None)
        self.assertIn("clean checkout", str(caught.exception))


class BashTests(Base):
    def test_an_old_bash_is_named_as_missing(self):
        calls = []
        with mock.patch.object(og.shutil, "which", lambda name: "/bin/true"), mock.patch.object(og, "bash_major", lambda: 3):
            with self.assertRaises(og.Refused) as caught:
                og.build("o/r", self.dir / "refs", True, self.pin, run=lambda *a, **k: calls.append(a))
        self.assertIn("bash>=5", str(caught.exception))
        self.assertEqual(calls, [])

    def test_bash_major_reads_the_version_line(self):
        fake = subprocess.CompletedProcess([], 0, stdout="GNU bash, version 5.3.20(1)-release\n")
        with mock.patch.object(og.subprocess, "run", lambda *a, **k: fake):
            self.assertEqual(og.bash_major(), 5)
        with mock.patch.object(og.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess([], 0, stdout="garbled")):
            self.assertEqual(og.bash_major(), 0)


class LinuxScriptTests(unittest.TestCase):
    SCRIPT = Path(__file__).resolve().parent / "build_linux_in_alpine.sh"

    def text(self):
        return self.SCRIPT.read_text(encoding="utf-8")

    def test_the_script_is_valid_shell(self):
        result = subprocess.run(["sh", "-n", str(self.SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_engines_libraries_come_from_its_own_target_without_no_cache(self):
        text = self.text()
        self.assertIn("make install-deps-ALPINE-for-semgrep-core", text)
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if "--no-cache" in line:
                for library in ("pcre2", "pkgconf", "gmp", "libev"):
                    self.assertNotIn(library, line, f"{library} must not be installed with --no-cache")

    def test_it_checks_nothing_in_unpinned_and_reads_the_ocaml_version_from_the_pin(self):
        text = self.text()
        pin = json.loads((Path(__file__).resolve().parent.parent / "references" / "source-pin.json").read_text(encoding="utf-8"))
        engine = next(s for s in pin["sources"] if s["slug"] == "opengrep/opengrep")
        self.assertIn(f'OCAML_VERSION:-{engine["build"]["ocaml"]}', text)
        self.assertNotIn("curl | ", text)
        self.assertNotIn("| sh", text)


class StatusTests(Base):
    def test_status_reports_pin_reference_and_missing_tools(self):
        lines = []
        with mock.patch.object(og.shutil, "which", lambda name: None):
            og.status("o/r", self.dir / "refs", self.pin, lines.append)
        text = "\n".join(lines)
        self.assertIn(SHA, text)
        self.assertIn("reference: absent", text)
        self.assertIn("missing opam", text)

    def test_cli_exit_codes(self):
        self.assertEqual(og.main(["status", "--slug", "o/r", "--pin-file", str(self.pin), "--root", str(self.dir)]), 0)
        self.assertEqual(og.main(["build", "--slug", "o/r", "--pin-file", str(self.pin), "--root", str(self.dir)]), 2)
        self.assertEqual(og.main(["status", "--slug", "x/y", "--pin-file", str(self.pin), "--root", str(self.dir)]), 2)


if __name__ == "__main__":
    unittest.main()
