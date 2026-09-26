"""Negative controls for tools/verify_pins.py.

Each control builds a small workspace in a temporary directory (gitlinks via
``git update-index --cacheinfo``, a hand-written .gitmodules and pins.json),
then runs the checker through its CLI with ``--repo`` and ``--pins`` so the
paths are resolved at call time. A control that must FAIL asserts a nonzero
exit; the committed real tree must PASS.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
CHECKER = os.path.join(WORKSPACE, "tools", "verify_pins.py")

SHA_A = "1111111111111111111111111111111111111111"
SHA_B = "2222222222222222222222222222222222222222"
SHA_C = "3333333333333333333333333333333333333333"


def git(args, cwd):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT="0")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x",
                    "-c", "commit.gpgsign=false"] + list(args),
                   cwd=cwd, check=True, capture_output=True, text=True, env=env)


def run_checker(repo, pins=None, extra=()):
    cmd = [sys.executable, CHECKER, "--repo", repo]
    if pins is not None:
        cmd += ["--pins", pins]
    cmd += list(extra)
    return subprocess.run(cmd, capture_output=True, text=True)


def entry(name, sha, opt_in=False, public=True):
    return {"name": name, "path": "repos/" + name,
            "url": "https://example.invalid/" + name + ".git",
            "default_branch": "main", "pinned_sha": sha,
            "public": public, "opt_in": opt_in, "note": "fixture"}


def build_fixture(root, gitlinks, modules, pins_entries):
    """gitlinks: {path: sha}; modules: {path: {url, branch[, update]}}."""
    git(["init", "-q", "-b", "main", root], cwd=root)
    lines = []
    for path, fields in modules.items():
        lines.append('[submodule "%s"]' % path)
        lines.append("\tpath = %s" % path)
        for k, v in fields.items():
            lines.append("\t%s = %s" % (k, v))
    with open(os.path.join(root, ".gitmodules"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    pins = os.path.join(root, "pins.json")
    with open(pins, "w") as fh:
        json.dump({"schema": "ulw.pins.v1", "generated_utc": "2026-01-01T00:00:00Z",
                   "repos": pins_entries}, fh)
    git(["add", ".gitmodules", "pins.json"], cwd=root)
    for path, sha in gitlinks.items():
        git(["update-index", "--add", "--cacheinfo",
             "160000,%s,%s" % (sha, path)], cwd=root)
    git(["commit", "-q", "-m", "fixture"], cwd=root)
    return pins


def consistent_parts():
    gitlinks = {"repos/a": SHA_A, "repos/b": SHA_B}
    modules = {
        "repos/a": {"url": "https://example.invalid/a.git", "branch": "main"},
        "repos/b": {"url": "https://example.invalid/b.git", "branch": "main",
                    "update": "none"},
    }
    pins = [entry("a", SHA_A), entry("b", SHA_B, opt_in=True, public=False)]
    return gitlinks, modules, pins


class VerifyPinsControls(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="ulw-test-")
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_consistent_fixture_passes(self):
        """The fixture builder itself yields a passing workspace, so the
        failures below are attributable to the single defect each injects."""
        pins = build_fixture(self.root, *consistent_parts())
        proc = run_checker(self.root, pins)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("verify_pins: OK", proc.stdout)

    def test_gitlink_sha_differs_from_pins_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        gitlinks["repos/a"] = SHA_C  # tree says C, pins.json says A
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/a: gitlink %s != pinned_sha %s" % (SHA_C, SHA_A),
                      proc.stdout)

    def test_prefix_match_is_not_accepted(self):
        gitlinks, modules, pins_entries = consistent_parts()
        gitlinks["repos/a"] = SHA_A[:-1] + "f"  # differs in the last hex digit
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)

    def test_update_none_without_opt_in_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        modules["repos/a"]["update"] = "none"  # pins say opt_in=false
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/a: .gitmodules has 'update = none' but pins "
                      "opt_in is false", proc.stdout)

    def test_opt_in_without_update_none_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        del modules["repos/b"]["update"]  # pins say opt_in=true
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/b: opt_in but .gitmodules lacks 'update = none'",
                      proc.stdout)

    def test_missing_gitlink_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        del gitlinks["repos/b"]  # listed in pins.json and .gitmodules only
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/b: no mode-160000 gitlink in HEAD tree",
                      proc.stdout)

    def test_unlisted_gitlink_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        gitlinks["repos/c"] = SHA_C  # in tree, absent from pins.json
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/c: gitlink in HEAD tree is not listed in "
                      "pins.json", proc.stdout)

    def test_url_or_branch_mismatch_fails(self):
        gitlinks, modules, pins_entries = consistent_parts()
        modules["repos/a"]["branch"] = "develop"
        pins = build_fixture(self.root, gitlinks, modules, pins_entries)
        proc = run_checker(self.root, pins)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("repos/a: .gitmodules branch 'develop' != "
                      "default_branch 'main'", proc.stdout)

    def test_flags_redirect_the_checker(self):
        """--pins pointing at a file that disagrees with an otherwise-good
        tree must fail: the checker reads the flag, not a baked-in path."""
        pins = build_fixture(self.root, *consistent_parts())
        other = os.path.join(self.root, "other.json")
        with open(other, "w") as fh:
            json.dump({"schema": "ulw.pins.v1", "generated_utc": "x",
                       "repos": [entry("a", SHA_C),
                                 entry("b", SHA_B, opt_in=True, public=False)]},
                      fh)
        self.assertEqual(run_checker(self.root, pins).returncode, 0)
        self.assertNotEqual(run_checker(self.root, other).returncode, 0)

    def test_committed_real_tree_passes(self):
        """The real workspace (parent of this tests/ directory) must pass
        without --network."""
        proc = run_checker(WORKSPACE)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("verify_pins: OK (8 pin(s)", proc.stdout)

    def test_readme_table_renders_pins_json(self):
        """README's table is a rendering of pins.json: every pinned SHA must
        appear as a full commit link, and no stale full SHA may remain."""
        import re
        with open(os.path.join(WORKSPACE, "pins.json"), encoding="utf-8") as fh:
            pins = json.load(fh)["repos"]
        with open(os.path.join(WORKSPACE, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        expected = set()
        for e in pins:
            link = "https://github.com/d6g8k5htny-coder/%s/commit/%s" % (
                e["name"], e["pinned_sha"])
            self.assertIn("[%s](%s)" % (e["pinned_sha"], link), readme)
            expected.add(e["pinned_sha"])
        found = set(re.findall(r"\b[0-9a-f]{40}\b", readme))
        self.assertEqual(found, expected)


if __name__ == "__main__":
    unittest.main()
