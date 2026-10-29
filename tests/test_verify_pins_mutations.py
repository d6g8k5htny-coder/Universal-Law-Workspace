"""Mutation controls for the strict cross-repository pin checker.

Each mutant removes one guard from a disposable copy of the checker. The
corresponding real-Git test must fail for an assertion, not a syntax/import
error. These controls cover the listed pin-checking faults, not Layer A.
"""
from pathlib import Path
import inspect
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TEST_CASE = "test_verify_pins_strict.StrictCurrentPinTests."
MUTANTS = (
    ("skip-private", 'errors.append("%s: not public; currentness was not checked" % path)',
     'info.append("%s: not public; currentness was not checked" % path)',
     "test_skipped_nonpublic_repository_is_rejected"),
    ("ignore-ls-remote-failure", '(errors if require_current else info).append(message)',
     'info.append(message)', "test_failed_remote_tip_lookup_is_rejected_after_successful_fetch"),
    ("allow-duplicate-refs", 'if len(defaults) > 1 or len(heads) > 1 or len(branch_tips) > 1:',
     'if False:', "test_duplicate_branch_advertisement_is_rejected"),
    ("allow-missing-default", 'errors.append("%s: remote default branch is unknown" % path)',
     'info.append("%s: remote default branch is unknown" % path)',
     "test_missing_default_branch_is_rejected"),
    ("allow-wrong-default", 'errors.append("%s: remote default branch %s does not match %s" %',
     'info.append("%s: remote default branch %s does not match %s" %',
     "test_wrong_default_branch_is_rejected_even_when_pin_matches_main"),
    ("allow-missing-head", 'errors.append("%s: remote HEAD commit is missing or malformed" % path)',
     'info.append("%s: remote HEAD commit is missing or malformed" % path)',
     "test_missing_head_commit_is_rejected_even_when_branch_tip_matches"),
    ("allow-missing-branch", 'errors.append("%s: configured branch %s tip is missing or malformed" %',
     'info.append("%s: configured branch %s tip is missing or malformed" %',
     "test_missing_configured_branch_is_rejected"),
    ("allow-inconsistent-head", 'errors.append("%s: remote HEAD and configured branch disagree" % path)',
     'info.append("%s: remote HEAD and configured branch disagree" % path)',
     "test_inconsistent_head_and_branch_advertisement_is_rejected"),
    ("allow-stale-tip", 'if branch_tips and branch_tips[0] != sha:',
     'if False:', "test_newer_remote_tip_is_rejected"),
    ("skip-remote-check", 'if (args.network or args.require_current) and not (args.require_current and errors):',
     'if args.network and not (args.require_current and errors):', "test_newer_remote_tip_is_rejected"),
    ("claim-unproved-ancestry", '%s: pin %s differs from tip %s of %s (informational)',
     '%s: pin %s is behind tip %s of %s (informational)',
     "test_legacy_tip_difference_does_not_claim_ancestry"),
    ("skip-preflight-inputs", 'initial_input_errors = check_committed_inputs(repo, pins_path, commit)',
     'initial_input_errors = []', "test_initial_manifest_mismatch_does_not_start_remote_lookup"),
    ("skip-final-inputs", 'final_input_errors = check_committed_inputs(repo, pins_path, commit)',
     'final_input_errors = []', "test_pin_manifest_change_during_lookup_is_rejected"),
    ("ignore-workspace-head-movement", 'if final_commit != commit:',
     'if False:', "test_workspace_head_change_during_lookup_is_rejected"),
    ("allow-symlinked-inputs", 'if os.path.islink(path):',
     'if False:', "test_symlinked_gitmodules_is_rejected_even_with_identical_bytes"),
)


from pin_mutation_receipts import intended_failure, pin_protocol, read_event


def run_case(root, test, *, event=None, nonce=None):
    flags = ["-B"] + (["-O"] if sys.flags.optimize else [])
    env = dict(os.environ)
    env.pop("CBZ_PIN_EVENT", None)
    env.pop("CBZ_PIN_NONCE", None)
    if event is not None:
        env["CBZ_PIN_EVENT"] = str(event)
        env["CBZ_PIN_NONCE"] = nonce
    return subprocess.run(
        [sys.executable, *flags, "-m", "unittest", "-v", TEST_CASE + test],
        cwd=root / "tests", env=env, capture_output=True, text=True)


def copy_controls(root):
    (root / "tools").mkdir()
    (root / "tests").mkdir()
    for filename in ("test_verify_pins.py", "test_verify_pins_strict.py",
                     "pin_mutation_receipts.py"):
        shutil.copyfile(ROOT / "tests" / filename, root / "tests" / filename)


class StrictPinMutationControls(unittest.TestCase):
    def test_all_named_guard_removals_are_detected(self):
        source = (ROOT / "tools/verify_pins.py").read_text(encoding="utf-8")
        self.assertEqual(len(MUTANTS), 15)
        for name, before, after, test in MUTANTS:
            with self.subTest(mutant=name):
                self.assertEqual(source.count(before), 1,
                                 "mutant target missing or ambiguous: " + name)
                baseline = run_case(ROOT, test)
                self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
                self.assertRegex(baseline.stdout + baseline.stderr, r"Ran 1 test in ")
                candidate = source.replace(before, after, 1)
                compile(candidate, "strict-pin-checker-mutant", "exec")
                with tempfile.TemporaryDirectory(prefix="cbz-pin-mutant-") as tmp:
                    root = Path(tmp)
                    copy_controls(root)
                    (root / "tools/verify_pins.py").write_text(candidate, encoding="utf-8")
                    event = root / "mutation-observation.json"
                    nonce = secrets.token_hex(16)
                    process = run_case(root, test, event=event, nonce=nonce)
                    self.assertTrue(intended_failure(process, test, nonce, read_event(event)),
                                    name + " did not fail for its intended policy outcome:\n" +
                                    process.stdout + process.stderr)


class StrictPinHarnessControls(unittest.TestCase):
    TEST = "test_skipped_nonpublic_repository_is_rejected"
    NONCE = "0" * 32

    @staticmethod
    def report(code=1, text=None):
        if text is None:
            text = ("FAIL: test_skipped_nonpublic_repository_is_rejected "
                    "(fixture.Test.test_skipped_nonpublic_repository_is_rejected)\n"
                    "Traceback (most recent call last)\nAssertionError: invalid input accepted\n"
                    "Ran 1 test in 0.1s\nFAILED (failures=1)\n")
        return subprocess.CompletedProcess([], code, stdout=text, stderr="")

    def event(self):
        return {"test": self.TEST, "event": "invalid-source-accepted", "nonce": self.NONCE}

    def test_actual_silent_checker_exit_cannot_count_as_a_kill(self):
        cases = {
            "silent86": "raise SystemExit(86)\n",
            "silent1": "raise SystemExit(1)\n",
            "silent0": "raise SystemExit(0)\n",
            "traceback": "raise RuntimeError('unrelated pin checker crash')\n",
            "unrelated-refusal": "print('FAIL: unrelated'); print('verify_pins: FAIL (1 error(s) across 1 pin(s))'); raise SystemExit(1)\n",
        }
        with tempfile.TemporaryDirectory(prefix="strict-pin-silent-checker-") as folder:
            root = Path(folder)
            copy_controls(root)
            checker = root / "tools/verify_pins.py"
            event = root / "mutation-observation.json"
            for label, source in cases.items():
                with self.subTest(checker=label):
                    checker.write_text(source)
                    event.unlink(missing_ok=True)
                    nonce = secrets.token_hex(16)
                    process = run_case(root, self.TEST, event=event, nonce=nonce)
                    self.assertFalse(intended_failure(process, self.TEST, nonce, read_event(event)),
                                     "unrelated strict-pin checker failure was credited")
                    self.assertFalse(event.exists(), "checker failure emitted policy-bypass evidence")

    def test_exact_named_observation_and_assertion_are_required(self):
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
                     good.stdout.replace("FAIL: " + self.TEST, "FAIL: other"),
                     good.stdout + "SyntaxError: unrelated\n"):
            self.assertFalse(intended_failure(self.report(text=text), self.TEST, self.NONCE, self.event()))

    def test_specific_demoted_reason_is_required_even_if_another_guard_refuses(self):
        from test_verify_pins_strict import StrictCurrentPinTests
        for method, reason in (
            ("test_missing_default_branch_is_rejected", "remote default branch is unknown"),
            ("test_missing_configured_branch_is_rejected", "configured branch main tip is missing"),
        ):
            for observed, expected in ((reason, True), ("unrelated diagnostic", False)):
                with self.subTest(method=method, observed=observed):
                    with tempfile.TemporaryDirectory() as folder:
                        event = Path(folder) / "event.json"
                        nonce = secrets.token_hex(16)
                        process = self.report(1, "info: repos/a: " + observed + "\\n"
                            + "FAIL: repos/a: independent guard refused\\n"
                            + "verify_pins: FAIL (1 error(s) across 1 pin(s))\\n")
                        process.cbz_protocol = pin_protocol(process)
                        case = StrictCurrentPinTests(method)
                        with patch.dict(os.environ, {"CBZ_PIN_EVENT": str(event),
                                                     "CBZ_PIN_NONCE": nonce}):
                            with self.assertRaises(AssertionError):
                                case.assert_refused(process, reason)
                        if expected:
                            self.assertEqual(read_event(event), {"test": method,
                                "event": "expected-policy-demoted", "nonce": nonce})
                        else:
                            self.assertFalse(event.exists())

    def test_pin_result_protocol_has_positive_and_crash_controls(self):
        self.assertEqual(pin_protocol(self.report(0, "verify_pins: OK (1 pin(s) agree)\n")), "accepted")
        self.assertEqual(pin_protocol(self.report(1,
            "FAIL: repos/a: invalid source\nverify_pins: FAIL (1 error(s) across 1 pin(s))\n")), "refused")
        for process in (self.report(86, ""), self.report(1, ""), self.report(0, ""),
                        self.report(1, "FAIL: unrelated without summary\n"),
                        self.report(1, "Traceback (most recent call last)\nverify_pins: FAIL (1)\n")):
            with self.assertRaisesRegex(RuntimeError, "pin checker"):
                pin_protocol(process)

    def test_four_actual_classifier_source_mutants_are_rejected(self):
        source = inspect.getsource(intended_failure)
        changes = [
            ("process.returncode == 1", "process.returncode != 0", self.report(86), self.event()),
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
                exec(compile(source.replace(before, after), "strict-pin-harness-mutant", "exec"), namespace)
                mutated = namespace["intended_failure"]
                case = unittest.FunctionTestCase(
                    lambda: self.assertFalse(mutated(process, self.TEST, self.NONCE, event)))
                result = unittest.TestResult()
                case.run(result)
                self.assertEqual(result.testsRun, 1)
                self.assertEqual(len(result.failures), 1)
                self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
