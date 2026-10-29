"""Mutation controls for canonical source identity verification."""
import os
import inspect
import io
import json
import re
import runpy
import secrets
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/verify_canonical_inputs.py"
CONTROLS = ROOT / "tests/test_verify_canonical_inputs.py"

# Each weakening is tied to an end-to-end test, using real disposable Git
# objects/remotes. A mutated checker must be rejected by an assertion, not by
# a syntax error, import error, or unexpected runtime exception.
MUTANTS = [
    ("wrong-blob", "if actual != blob:", "if False:", "test_wrong_current_blob_fails"),
    ("nonregular-source", 'if mode not in ("100644", "100755") or kind != "blob":',
     "if False:", "test_symlinked_source_is_not_accepted_as_a_blob"),
    ("empty-source-set", "if not isinstance(inputs, dict) or not inputs:",
     "if not isinstance(inputs, dict):", "test_empty_canonical_inputs_fails"),
    ("workspace-membership", "or name not in names or name not in remote_map:",
     "or name not in remote_map:", "test_pinned_repository_must_be_listed_in_workspace"),
    ("skip-nonpublic", 'if not pin.get("public"):', "if False:",
     "test_nonpublic_source_cannot_be_skipped"),
    ("working-input-bytes", "if expected != actual:", "if False:",
     "test_dirty_workspace_manifest_fails"),
    ("working-input-symlink", "if path.resolve() != path or not path.is_file():",
     "if not path.is_file():", "test_identical_symlinked_workspace_manifest_fails"),
    ("gitlink-binding", "errors.extend(check_tree_and_modules(repo, pins, head))",
     "errors.extend([])", "test_gitlink_mismatch_fails"),
    ("historical-source", 'ref = item.get("ref", remote_map[name]["pinned_sha"])',
     'ref = remote_map[name]["pinned_sha"]', "test_current_and_explicit_historical_sources_pass"),
    ("unsupported-history-label", '"separate-ref" if "ref" in item',
     '"historical" if "ref" in item', "test_explicit_newer_commit_is_not_called_historical"),
    ("fetched-commit", "if got != commit:", "if False:",
     "test_fetched_commit_identity_mismatch_fails"),
    ("moving-head", "if end_head != head:", "if False:",
     "test_workspace_head_change_during_fetch_fails"),
    ("input-recheck", "for name in INPUTS:\n            if committed_input(repo, head, name) != snapshot[name]:",
     "for name in ():\n            if committed_input(repo, head, name) != snapshot[name]:",
     "test_manifest_change_during_fetch_fails"),
]


def intended_failure(result, test, nonce, event):
    output = result.stdout + result.stderr
    kind = {"test_current_and_explicit_historical_sources_pass": "historical-source-ignored",
            "test_explicit_newer_commit_is_not_called_historical": "separate-ref-mislabeled"}.get(
                test, "invalid-source-accepted")
    expected = {"test": test, "event": kind, "nonce": nonce}
    return (result.returncode == 1
            and type(nonce) is str and re.fullmatch(r"[0-9a-f]{32}", nonce) is not None
            and type(event) is dict and event == expected
            and re.search(r"^Ran 1 test in ", output, re.M) is not None
            and re.search(r"^FAIL: " + re.escape(test) + r"[ (]", output, re.M) is not None
            and re.search(r"^FAILED \(failures=1\)$", output, re.M) is not None
            and "ERROR:" not in output and "SyntaxError:" not in output
            and output.count("Traceback (most recent call last)") == 1)


def read_event(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError):
        return None


class CanonicalHarnessControls(unittest.TestCase):
    TEST = "test_wrong_current_blob_fails"
    NONCE = "0" * 32

    @staticmethod
    def report(code=1, text=None):
        if text is None:
            text = ("FAIL: test_wrong_current_blob_fails (fixture.Test.test_wrong_current_blob_fails)\n"
                    "Traceback (most recent call last)\nAssertionError: invalid input was accepted\n"
                    "Ran 1 test in 0.1s\nFAILED (failures=1)\n")
        return subprocess.CompletedProcess([], code, stdout=text, stderr="")

    def event(self):
        return {"test": self.TEST, "event": "invalid-source-accepted", "nonce": self.NONCE}

    def test_actual_silent_checker_exit_is_not_a_mutation_kill(self):
        flags = ["-B"] + (["-O"] if sys.flags.optimize else [])
        cases = {
            "silent86": "raise SystemExit(86)\n",
            "silent1": "raise SystemExit(1)\n",
            "silent0": "raise SystemExit(0)\n",
            "traceback": "raise RuntimeError('unrelated checker crash')\n",
            "wrong-diagnostic": "print('FAIL: unrelated refusal'); raise SystemExit(1)\n",
        }
        with tempfile.TemporaryDirectory(prefix="canonical-silent-crash-") as folder:
            checker = Path(folder) / "verify_canonical_inputs.py"
            receipt = Path(folder) / "observation.json"
            for label, source in cases.items():
                with self.subTest(checker=label):
                    checker.write_text(source)
                    receipt.unlink(missing_ok=True)
                    nonce = secrets.token_hex(16)
                    env = dict(os.environ, CBZ_CANONICAL_CHECKER=str(checker),
                               CBZ_CANONICAL_EVENT=str(receipt), CBZ_CANONICAL_NONCE=nonce)
                    process = subprocess.run(
                        [sys.executable, *flags, str(CONTROLS),
                         "CanonicalInputControls." + self.TEST, "-q"],
                        env=env, text=True, capture_output=True)
                    self.assertFalse(intended_failure(process, self.TEST, nonce, read_event(receipt)),
                                     "checker crash or unrelated refusal counted as an intended kill")
                    self.assertFalse(receipt.exists(), "unrelated checker failure emitted bypass evidence")

    def test_exact_named_control_event_and_assertion_are_required(self):
        good = self.report()
        self.assertTrue(intended_failure(good, self.TEST, self.NONCE, self.event()))
        for code in (0, 2, 86):
            self.assertFalse(intended_failure(self.report(code), self.TEST, self.NONCE, self.event()))
        for event in (None, {}, {**self.event(), "nonce": "1" * 32},
                      {**self.event(), "test": "other"}, {**self.event(), "event": "other"},
                      {**self.event(), "extra": True}):
            self.assertFalse(intended_failure(good, self.TEST, self.NONCE, event))
        for text in (good.stdout.replace("Ran 1 test", "Ran 0 tests"),
                     good.stdout.replace("failures=1", "errors=1"),
                     good.stdout.replace("failures=1", "failures=1, errors=1"),
                     good.stdout.replace("failures=1", "failures=1, skipped=1"),
                     good.stdout.replace("FAIL: test_wrong_current_blob_fails", "FAIL: other"),
                     good.stdout + "SyntaxError: invalid source\n"):
            self.assertFalse(intended_failure(self.report(text=text), self.TEST, self.NONCE, self.event()))

    def test_checker_result_protocol_has_positive_and_crash_controls(self):
        protocol = runpy.run_path(str(CONTROLS))["checker_protocol"]
        self.assertEqual(protocol(self.report(0,
            "verify_canonical_inputs: OK (2 canonical inputs; default-tip currency is separate)\n")), "accepted")
        self.assertEqual(protocol(self.report(1, "FAIL: source blob differs\n")), "refused")
        for process in (self.report(86, ""), self.report(1, ""), self.report(0, ""),
                        self.report(1, "Traceback (most recent call last)\nFAIL: misleading\n")):
            with self.assertRaisesRegex(RuntimeError, "checker"):
                protocol(process)

    def test_four_actual_harness_source_mutants_are_rejected(self):
        source = inspect.getsource(intended_failure)
        changes = [
            ("result.returncode == 1", "result.returncode != 0", self.report(86), self.event()),
            ("type(event) is dict and event == expected", "True", self.report(), None),
            ('re.search(r"^Ran 1 test in ", output, re.M) is not None', "True",
             self.report(text=self.report().stdout.replace("Ran 1 test", "Ran 0 tests")), self.event()),
            ('"test": test, "event": kind', '"test": event.get("test"), "event": kind',
             self.report(), {**self.event(), "test": "other"}),
        ]
        for before, after, process, event in changes:
            with self.subTest(guard=before):
                self.assertEqual(source.count(before), 1)
                namespace = {"re": re}
                exec(compile(source.replace(before, after), "canonical-harness-mutant", "exec"), namespace)
                mutated = namespace["intended_failure"]
                case = unittest.FunctionTestCase(
                    lambda: self.assertFalse(mutated(process, self.TEST, self.NONCE, event)))
                result = unittest.TestResult()
                case.run(result)
                self.assertEqual(result.testsRun, 1)
                self.assertEqual(len(result.failures), 1)
                self.assertEqual(result.errors, [])


class CanonicalMutationControls(unittest.TestCase):
    def test_all_named_guard_mutations_are_detected(self):
        flags = ["-B"] + (["-O"] if sys.flags.optimize else [])
        env = dict(os.environ)
        env.pop("CBZ_CANONICAL_CHECKER", None)
        base = subprocess.run([sys.executable, *flags, str(CONTROLS), "-q"],
                              env=env, text=True, capture_output=True)
        self.assertEqual(base.returncode, 0, base.stdout + base.stderr)
        source = CHECKER.read_text()
        with tempfile.TemporaryDirectory(prefix="canonical-mutants-") as tmp:
            folder = Path(tmp)
            shutil.copy2(ROOT / "tools/verify_pins.py", folder / "verify_pins.py")
            target = folder / "verify_canonical_inputs.py"
            env["CBZ_CANONICAL_CHECKER"] = str(target)
            for label, old, new, test in MUTANTS:
                with self.subTest(mutation=label):
                    self.assertEqual(source.count(old), 1, "stale mutation " + label)
                    weakened = source.replace(old, new, 1)
                    compile(weakened, str(target), "exec")
                    target.write_text(weakened)
                    receipt = folder / "observation.json"
                    receipt.unlink(missing_ok=True)
                    nonce = secrets.token_hex(16)
                    env["CBZ_CANONICAL_EVENT"] = str(receipt)
                    env["CBZ_CANONICAL_NONCE"] = nonce
                    result = subprocess.run(
                        [sys.executable, *flags, str(CONTROLS),
                         "CanonicalInputControls." + test, "-q"],
                        env=env, text=True, capture_output=True)
                    output = result.stdout + result.stderr
                    self.assertTrue(intended_failure(result, test, nonce, read_event(receipt)),
                                    "not a specific behavioral kill: " + label + "\n" + output)


if __name__ == "__main__":
    unittest.main()
