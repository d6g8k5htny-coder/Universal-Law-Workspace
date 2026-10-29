"""Current-tip admission checks against disposable, real local Git remotes.

These tests exercise the CLI; the lookup-failure and inconsistent-advertising
cases substitute only the external Git response and still run real fetches.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_verify_pins import CHECKER, build_fixture, entry, git, run_checker


class StrictCurrentPinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cbz-strict-pins-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote"
        self.remote.mkdir()
        git(["init", "-q", "-b", "main", str(self.remote)], cwd=self.root)
        git(["commit", "-q", "--allow-empty", "-m", "initial"], cwd=self.remote)
        self.pin = git(["rev-parse", "HEAD"], cwd=self.remote).stdout.strip()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.e = entry("a", self.pin)
        self.e["url"] = str(self.remote)

    def make_workspace(self):
        modules = {self.e["path"]: {"url": self.e["url"], "branch": "main"}}
        self.pins = build_fixture(str(self.workspace),
                                  {self.e["path"]: self.pin}, modules, [self.e])

    def run_strict(self, env=None):
        flags = ["-E"] + (["-O"] if sys.flags.optimize else [])
        cmd = [sys.executable] + flags + [CHECKER, "--repo", str(self.workspace),
               "--pins", self.pins, "--require-current"]
        return subprocess.run(cmd, capture_output=True, text=True, env=env)

    def assert_refused(self, process, reason):
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("FAIL:", process.stdout)
        self.assertTrue(any(line.startswith("FAIL: repos/a: ") and reason in line
                            for line in process.stdout.splitlines()),
                        process.stdout + process.stderr)
        self.assertNotIn("verify_pins: OK", process.stdout)

    def test_matching_public_default_and_branch_are_accepted(self):
        self.make_workspace()
        process = self.run_strict()
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("verify_pins: OK", process.stdout)

    def test_newer_remote_tip_is_rejected(self):
        self.make_workspace()
        git(["commit", "-q", "--allow-empty", "-m", "new tip"], cwd=self.remote)
        legacy = run_checker(str(self.workspace), self.pins, extra=("--network",))
        self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)
        self.assert_refused(self.run_strict(), "does not match")

    def test_legacy_tip_difference_does_not_claim_ancestry(self):
        self.make_workspace()
        git(["branch", "saved-pin"], cwd=self.remote)
        git(["checkout", "--orphan", "unrelated"], cwd=self.remote)
        git(["commit", "-q", "--allow-empty", "-m", "unrelated root"], cwd=self.remote)
        unrelated = git(["rev-parse", "HEAD"], cwd=self.remote).stdout.strip()
        git(["update-ref", "refs/heads/main", unrelated], cwd=self.remote)
        git(["symbolic-ref", "HEAD", "refs/heads/main"], cwd=self.remote)
        ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", self.pin, unrelated],
                                  cwd=self.remote, capture_output=True)
        self.assertEqual(ancestry.returncode, 1)
        flags = ("-E",) + (("-O",) if sys.flags.optimize else ())
        process = run_checker(str(self.workspace), self.pins, extra=("--network",),
                              python_args=flags)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("differs from tip", process.stdout)
        self.assertNotIn("is behind tip", process.stdout)

    def test_missing_default_branch_is_rejected(self):
        self.make_workspace()
        git(["symbolic-ref", "HEAD", "refs/heads/unborn"], cwd=self.remote)
        self.assert_refused(self.run_strict(), "remote default branch is unknown")

    def test_wrong_default_branch_is_rejected_even_when_pin_matches_main(self):
        self.make_workspace()
        git(["branch", "other"], cwd=self.remote)
        git(["symbolic-ref", "HEAD", "refs/heads/other"], cwd=self.remote)
        self.assert_refused(self.run_strict(), "remote default branch refs/heads/other does not match")

    def test_missing_configured_branch_is_rejected(self):
        self.make_workspace()
        git(["branch", "-m", "archive"], cwd=self.remote)
        self.assert_refused(self.run_strict(), "configured branch main tip is missing")

    def test_skipped_nonpublic_repository_is_rejected(self):
        self.e["public"] = False
        self.make_workspace()
        self.assert_refused(self.run_strict(), "not public")

    def test_working_pins_cannot_mask_a_different_committed_manifest(self):
        self.make_workspace()
        path = Path(self.pins)
        original = path.read_text()
        document = json.loads(original)
        document["repos"][0]["pinned_sha"] = "f" * 40
        path.write_text(json.dumps(document))
        git(["add", "pins.json"], cwd=self.workspace)
        git(["commit", "-q", "-m", "committed disagreement"], cwd=self.workspace)
        path.write_text(original)
        process = self.run_strict()
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("committed pins.json", process.stdout)

    def test_working_gitmodules_cannot_mask_committed_mismatch(self):
        self.make_workspace()
        path = self.workspace / ".gitmodules"
        original = path.read_text()
        path.write_text(original.replace(str(self.remote), str(self.root / "other")))
        git(["add", ".gitmodules"], cwd=self.workspace)
        git(["commit", "-q", "-m", "committed disagreement"], cwd=self.workspace)
        path.write_text(original)
        process = self.run_strict()
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("committed .gitmodules", process.stdout)

    def test_initial_manifest_mismatch_does_not_start_remote_lookup(self):
        self.make_workspace()
        Path(self.pins).write_text(Path(self.pins).read_text() + " ")
        env = self.git_shim('touch "$CBZ_MARKER"; exec "$CBZ_REAL_GIT" "$@"')
        marker = self.root / "lookup-started"
        env["CBZ_MARKER"] = str(marker)
        process = self.run_strict(env)
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("committed pins.json", process.stdout)
        self.assertFalse(marker.exists(), "invalid source unexpectedly contacted the remote")

    def test_symlinked_gitmodules_is_rejected_even_with_identical_bytes(self):
        self.make_workspace()
        path = self.workspace / ".gitmodules"
        copy = self.root / "gitmodules-copy"
        copy.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(copy)
        process = self.run_strict()
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("working .gitmodules is a symlink", process.stdout)

    def git_shim(self, lookup_body):
        shim_dir = self.root / "bin"
        shim_dir.mkdir()
        shim = shim_dir / "git"
        shim.write_text("#!/bin/sh\nif [ \"$1\" = ls-remote ]; then\n" +
                        lookup_body + "\nfi\nexec \"$CBZ_REAL_GIT\" \"$@\"\n")
        shim.chmod(0o755)
        env = dict(os.environ)
        env["CBZ_REAL_GIT"] = shutil.which("git")
        env["PATH"] = str(shim_dir) + os.pathsep + env["PATH"]
        return env

    def test_failed_remote_tip_lookup_is_rejected_after_successful_fetch(self):
        self.make_workspace()
        env = self.git_shim("echo lookup-failed >&2; exit 9")
        self.assert_refused(self.run_strict(env), "ls-remote")

    def test_workspace_head_change_during_lookup_is_rejected(self):
        self.make_workspace()
        body = ('"$CBZ_REAL_GIT" -C "$CBZ_TARGET_WS" -c user.name=t '
                '-c user.email=t@x -c commit.gpgsign=false commit -q '
                '--allow-empty -m changed; exec "$CBZ_REAL_GIT" "$@"')
        env = self.git_shim(body)
        env["CBZ_TARGET_WS"] = str(self.workspace)
        process = self.run_strict(env)
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("HEAD changed", process.stdout)

    def test_pin_manifest_change_during_lookup_is_rejected(self):
        self.make_workspace()
        body = 'printf " " >> "$CBZ_TARGET_WS/pins.json"; exec "$CBZ_REAL_GIT" "$@"'
        env = self.git_shim(body)
        env["CBZ_TARGET_WS"] = str(self.workspace)
        process = self.run_strict(env)
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("committed pins.json", process.stdout)

    def test_inconsistent_head_and_branch_advertisement_is_rejected(self):
        self.make_workspace()
        fake_head = "1" * 40 if self.pin != "1" * 40 else "2" * 40
        body = ("printf '%%s\\n' 'ref: refs/heads/main\tHEAD' "
                "'%s\tHEAD' '%s\trefs/heads/main'; exit 0" %
                (fake_head, self.pin))
        self.assert_refused(self.run_strict(self.git_shim(body)), "HEAD")

    def test_missing_head_commit_is_rejected_even_when_branch_tip_matches(self):
        self.make_workspace()
        body = ("printf '%%s\\n' 'ref: refs/heads/main\tHEAD' "
                "'%s\trefs/heads/main'; exit 0" % self.pin)
        self.assert_refused(self.run_strict(self.git_shim(body)),
                            "remote HEAD commit is missing")

    def test_duplicate_branch_advertisement_is_rejected(self):
        self.make_workspace()
        fake_tip = "1" * 40 if self.pin != "1" * 40 else "2" * 40
        body = ("printf '%%s\\n' 'ref: refs/heads/main\tHEAD' '%s\tHEAD' "
                "'%s\trefs/heads/main' '%s\trefs/heads/main'; exit 0" %
                (self.pin, self.pin, fake_tip))
        self.assert_refused(self.run_strict(self.git_shim(body)), "duplicate")


if __name__ == "__main__":
    unittest.main()
