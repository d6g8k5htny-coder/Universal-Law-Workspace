"""Handled pin-input type refusals; local fixtures only, no remote fetches."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


CHECKER = Path(__file__).resolve().parents[1] / "tools" / "verify_pins.py"
spec = importlib.util.spec_from_file_location("pins_input_types", CHECKER)
pins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pins)


def entry(**changes):
    row = dict(name="a", path="repos/a", url="https://example.invalid/a.git",
               default_branch="main", pinned_sha="1" * 40,
               public=False, opt_in=True, note="local test only")
    row.update(changes)
    return row


def manifest(*rows):
    return dict(schema="ulw.pins.v1", repos=list(rows))


class PinInputTypeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ulw-input-types-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.input = self.root / "pins.json"
        self.env = dict(os.environ)
        for key in ("PYTHONOPTIMIZE", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
            self.env.pop(key, None)
        self.flags = ["-B", "-S"] + (["-O"] if sys.flags.optimize else [])

    def write(self, value):
        self.input.write_text(json.dumps(value), encoding="utf-8")

    def cli(self, network=False, git_available=False):
        env = dict(self.env)
        if not git_available:
            # If validation incorrectly reaches Git, it cannot find an executable.
            env["PATH"] = str(self.root / "no-programs")
        command = [sys.executable, *self.flags, str(CHECKER),
                   "--repo", str(self.root), "--pins", str(self.input)]
        if network:
            command.append("--network")
        return subprocess.run(command, cwd=self.root, env=env,
                              stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, encoding="utf-8", timeout=10)

    def assert_handled(self, process, diagnostic):
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertIn("FAIL: " + diagnostic, process.stdout)
        self.assertIn("verify_pins: FAIL (", process.stdout)
        self.assertNotIn("verify_pins: OK", process.stdout)
        self.assertEqual(process.stderr, "")

    def test_nonobject_roots_are_handled(self):
        for value in (None, False, 7, 1.5, "root", []):
            with self.subTest(value=value):
                self.write(value)
                self.assert_handled(self.cli(network=True),
                                    "pins.json: root must be an object")

    def test_nonobject_entries_are_handled(self):
        for value in (None, False, 7, 1.5, "entry", []):
            with self.subTest(value=value):
                self.write(manifest(entry(), value))
                self.assert_handled(self.cli(network=True),
                                    "pins.json: entry 1 must be an object")

    def test_nonstring_or_empty_paths_are_handled(self):
        for value in (None, False, 7, 1.5, [], {}, ""):
            with self.subTest(value=value):
                self.write(manifest(entry(path=value)))
                self.assert_handled(self.cli(network=True),
                                    "pins.json: entry 0: 'path' must be a non-empty string")

    def test_valid_manifest_and_input_bytes_are_preserved(self):
        rows = [entry(), entry(name="b", path="repos/b", public=True, opt_in=False)]
        self.write(manifest(*rows))
        before = self.input.read_bytes()
        loaded, errors = pins.load_pins(self.input)
        self.assertEqual(loaded, rows)
        self.assertEqual(errors, [])
        self.assertEqual(self.input.read_bytes(), before)

    def test_existing_refusals_remain_handled(self):
        specimens = [
            ('{"schema":"ulw.pins.v1","repos":[],"repos":[]}',
             "pins.json: duplicate JSON member 'repos'"),
            (json.dumps(dict(schema="wrong", repos=[])), "pins.json: schema is"),
            (json.dumps(manifest()), "pins.json: 'repos' must be a non-empty list"),
            (json.dumps(manifest(dict(path="repos/a"))), "pins.json: entry 0 missing 'name'"),
            (json.dumps(manifest(entry(pinned_sha="A" * 40))),
             "pins.json: repos/a: pinned_sha '" + "A" * 40 + "' is not a full lowercase 40-hex SHA"),
            (json.dumps(manifest(entry(public=1))), "pins.json: repos/a: 'public' must be a boolean"),
            (json.dumps(manifest(entry(), entry())), "pins.json: duplicate path 'repos/a'"),
        ]
        for raw, diagnostic in specimens:
            with self.subTest(diagnostic=diagnostic):
                self.input.write_text(raw, encoding="utf-8")
                self.assert_handled(self.cli(network=True), diagnostic)

    def test_mixed_bad_entries_retain_later_diagnostics_and_do_not_reach_git(self):
        self.write(manifest(None, entry(path=[]), entry(public=1)))
        output = io.StringIO()
        with patch.object(pins, "run_git", side_effect=AssertionError("Git reached")) as git:
            with patch.object(pins, "check_network", side_effect=AssertionError("network reached")) as network:
                with contextlib.redirect_stdout(output):
                    try:
                        code = pins.main(["--repo", str(self.root), "--network"])
                    except (TypeError, AttributeError) as exc:
                        self.fail("Unhandled input type: " + repr(exc))
                self.assertEqual(code, 1)
                git.assert_not_called()
                network.assert_not_called()
        text = output.getvalue()
        self.assertIn("entry 0 must be an object", text)
        self.assertIn("entry 1: 'path' must be a non-empty string", text)
        self.assertIn("'public' must be a boolean", text)
        self.assertIn("3 error(s) across 3 pin(s)", text)

    def test_unexpected_programming_error_is_not_hidden(self):
        with patch.object(pins, "load_pins", side_effect=TypeError("programmer sentinel")):
            with self.assertRaisesRegex(TypeError, "programmer sentinel"):
                pins.main(["--repo", str(self.root)])

    def test_valid_local_git_tree_and_wrong_pin_control(self):
        git = shutil.which("git")
        self.assertIsNotNone(git, "This CLI integration test requires local Git")
        env = dict(self.env, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_AUTHOR_NAME="Local fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Local fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            env.pop(key, None)
        def run(*args):
            result = subprocess.run([git, *args], cwd=self.root, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        run("init", "-q")
        (self.root / ".gitmodules").write_text(
            '[submodule "repos/a"]\n\tpath = repos/a\n'
            '\turl = https://example.invalid/a.git\n\tbranch = main\n\tupdate = none\n',
            encoding="utf-8")
        self.write(manifest(entry()))
        run("add", ".gitmodules", "pins.json")
        run("update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",repos/a")
        run("-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull,
            "commit", "-qm", "Disposable pointer fixture")
        self.env = env
        good = self.cli(network=True, git_available=True)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertIn("verify_pins: OK (1 pin(s) agree", good.stdout)
        self.assertIn("not public; network check skipped", good.stdout)
        self.assertEqual(good.stderr, "")
        self.write(manifest(entry(pinned_sha="2" * 40)))
        bad = self.cli(git_available=True)
        self.assert_handled(bad, "repos/a: gitlink " + "1" * 40 + " != pinned_sha " + "2" * 40)


if __name__ == "__main__":
    unittest.main()
