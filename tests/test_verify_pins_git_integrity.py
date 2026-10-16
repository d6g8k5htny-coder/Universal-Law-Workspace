"""Pin verifier Git repository-routing and replacement-ref controls.

All fixtures are disposable local Git repositories. No outside network, real
submodule remote, production pin or user repository is touched. These checks
exercise the real command-line verifier, not a mocked subprocess response.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECKER = Path(__file__).resolve().parents[1] / "tools" / "verify_pins.py"
GOOD = "2" * 40
BAD = "1" * 40


def safe_environment():
    env = {name: value for name, value in os.environ.items()
           if not name.startswith(("GIT_", "PYTHON")) and name not in ("BASH_ENV", "ENV")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Disposable Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Disposable Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    return env


def run(*args, cwd=None, env=None, require_ok=True):
    completed = subprocess.run(args, cwd=cwd, env=env or safe_environment(),
                               capture_output=True, text=True, stdin=subprocess.DEVNULL,
                               check=False, timeout=30)
    if require_ok and completed.returncode:
        raise AssertionError((args, completed.returncode,
                              completed.stdout, completed.stderr))
    return completed


def git(where, *args, env=None):
    return run("git", *args, cwd=where, env=env)


def create_workspace(where, gitlink, pin, *, url="https://example.invalid/a.git",
                     public=False):
    where.mkdir(parents=True)
    git(where, "init", "-q", "-b", "main")
    (where / ".gitmodules").write_text(
        '[submodule "a"]\n\tpath = repos/a\n\turl = ' + url +
        '\n\tbranch = main\n\tupdate = none\n', encoding="utf-8")
    (where / "pins.json").write_text(json.dumps({
        "schema": "ulw.pins.v1", "repos": [{"name": "a", "path": "repos/a",
        "url": url, "default_branch": "main", "pinned_sha": pin,
        "public": public, "opt_in": True, "note": "disposable fixture"}]
    }), encoding="utf-8")
    git(where, "add", ".gitmodules", "pins.json")
    git(where, "update-index", "--add", "--cacheinfo",
        "160000," + gitlink + ",repos/a")
    git(where, "-c", "commit.gpgsign=false", "commit", "-qm", "initial fixture")
    return git(where, "rev-parse", "HEAD").stdout.strip()


class GitIntegrityControls(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix="ulw-git-integrity-")
        self.addCleanup(self.root.cleanup)
        self.location = Path(self.root.name)

    def verify(self, repo, *, extra_env=None, network=False):
        flags = ["-B", "-S"] + (["-O"] if sys.flags.optimize else [])
        env = safe_environment()
        if extra_env:
            env.update(extra_env)
        return run(sys.executable, *flags, str(CHECKER), "--repo", str(repo),
                   "--pins", str(repo / "pins.json"),
                   *(["--network"] if network else []), cwd=repo, env=env,
                   require_ok=False)

    def assert_rejected_mismatch(self, proc, *, expected=BAD, pinned=GOOD):
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn(f"gitlink {expected} != pinned_sha {pinned}", proc.stdout)
        self.assertIn("verify_pins: FAIL", proc.stdout)
        self.assertNotIn("Traceback", proc.stderr)

    def test_clean_valid_and_mismatched_checkout(self):
        good = self.location / "good"
        bad = self.location / "bad"
        create_workspace(good, GOOD, GOOD)
        create_workspace(bad, BAD, GOOD)
        p = self.verify(good)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("verify_pins: OK", p.stdout)
        self.assert_rejected_mismatch(self.verify(bad))

    def test_inherited_git_dir_cannot_select_foreign_head(self):
        selected = self.location / "selected"
        foreign = self.location / "foreign"
        create_workspace(selected, BAD, GOOD)
        create_workspace(foreign, GOOD, GOOD)
        self.assertEqual(self.verify(foreign).returncode, 0)
        self.assert_rejected_mismatch(self.verify(selected, extra_env={
            "GIT_DIR": str(foreign / ".git")}))

    def test_combined_git_routing_overrides_cannot_select_foreign_head(self):
        selected = self.location / "selected"
        foreign = self.location / "foreign"
        create_workspace(selected, BAD, GOOD)
        create_workspace(foreign, GOOD, GOOD)
        self.assert_rejected_mismatch(self.verify(selected, extra_env={
            "GIT_DIR": str(foreign / ".git"),
            "GIT_WORK_TREE": str(foreign),
            "GIT_INDEX_FILE": str(foreign / ".git" / "index")}))

    def test_local_replace_ref_cannot_substitute_committed_head_tree(self):
        selected = self.location / "selected"
        original = create_workspace(selected, GOOD, GOOD)
        git(selected, "update-index", "--add", "--cacheinfo", "160000," + BAD + ",repos/a")
        git(selected, "-c", "commit.gpgsign=false", "commit", "-qm", "mismatch")
        altered = git(selected, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(original, altered)
        git(selected, "replace", altered, original)
        raw = git(selected, "ls-tree", "-r", "HEAD", env=dict(safe_environment(),
                     GIT_NO_REPLACE_OBJECTS="1")).stdout
        swapped = git(selected, "ls-tree", "-r", "HEAD").stdout
        self.assertIn(BAD + "\trepos/a", raw)
        self.assertIn(GOOD + "\trepos/a", swapped)
        self.assert_rejected_mismatch(self.verify(selected))
        self.assert_rejected_mismatch(self.verify(selected, extra_env={
            "GIT_REPLACE_REF_BASE": "refs/replace"}))
        git(selected, "replace", "-d", altered)
        self.assert_rejected_mismatch(self.verify(selected))

    def test_offline_network_mode_rejects_foreign_git_dir_without_side_effect(self):
        remote = self.location / "remote"
        remote.mkdir()
        git(remote, "init", "-q", "-b", "main")
        (remote / "note.txt").write_text("disposable offline remote\n")
        git(remote, "add", "note.txt")
        git(remote, "-c", "commit.gpgsign=false", "commit", "-qm", "remote")
        pin = git(remote, "rev-parse", "HEAD").stdout.strip()
        selected = self.location / "selected"
        foreign = self.location / "foreign"
        create_workspace(selected, BAD, pin, url=str(remote), public=True)
        create_workspace(foreign, pin, pin, url=str(remote), public=True)
        foreign_fetch = foreign / ".git" / "FETCH_HEAD"
        self.assertFalse(foreign_fetch.exists())
        self.assert_rejected_mismatch(
            self.verify(selected, extra_env={"GIT_DIR": str(foreign / ".git")}, network=True),
            pinned=pin)
        self.assertFalse(foreign_fetch.exists(), "foreign FETCH_HEAD was mutated")
        clean = self.verify(foreign, network=True)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertIn("remotes checked", clean.stdout)

    def test_offline_network_valid_selected_checkout_ignores_foreign_dir(self):
        remote = self.location / "remote"
        remote.mkdir()
        git(remote, "init", "-q", "-b", "main")
        (remote / "note.txt").write_text("disposable remote fixture\n")
        git(remote, "add", "note.txt")
        git(remote, "-c", "commit.gpgsign=false", "commit", "-qm", "remote")
        pin = git(remote, "rev-parse", "HEAD").stdout.strip()
        selected = self.location / "selected"
        foreign = self.location / "foreign"
        create_workspace(selected, pin, pin, url=str(remote), public=True)
        create_workspace(foreign, BAD, pin, url=str(remote), public=True)
        fetched = foreign / ".git" / "FETCH_HEAD"
        p = self.verify(selected, extra_env={"GIT_DIR": str(foreign / ".git")}, network=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("remotes checked", p.stdout)
        self.assertFalse(fetched.exists(), "foreign FETCH_HEAD changed")


if __name__ == "__main__":
    unittest.main()
