"""Mutation controls for the strict cross-repository pin checker.

Each mutant removes one guard from a disposable copy of the checker. The
corresponding real-Git test must fail for an assertion, not a syntax/import
error. These controls cover the listed pin-checking faults, not Layer A.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


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


class StrictPinMutationControls(unittest.TestCase):
    def test_all_named_guard_removals_are_detected(self):
        source = (ROOT / "tools" / "verify_pins.py").read_text(encoding="utf-8")
        flags = ["-O"] if sys.flags.optimize else []
        for name, before, after, test_name in MUTANTS:
            with self.subTest(mutant=name):
                self.assertEqual(source.count(before), 1,
                                 "mutant target missing or ambiguous: " + name)
                with tempfile.TemporaryDirectory(prefix="cbz-pin-mutant-") as tmp:
                    root = Path(tmp)
                    (root / "tools").mkdir()
                    (root / "tests").mkdir()
                    (root / "tools" / "verify_pins.py").write_text(
                        source.replace(before, after, 1), encoding="utf-8")
                    for filename in ("test_verify_pins.py", "test_verify_pins_strict.py"):
                        shutil.copyfile(ROOT / "tests" / filename, root / "tests" / filename)
                    proc = subprocess.run(
                        [sys.executable] + flags + ["-m", "unittest", "-v", TEST_CASE + test_name],
                        cwd=root / "tests", capture_output=True, text=True)
                    result = proc.stdout + proc.stderr
                    self.assertEqual(proc.returncode, 1, name + " was not rejected:\n" + result)
                    self.assertIn("FAIL: " + test_name, result)
                    self.assertIn("FAILED (failures=1)", result)
                    self.assertNotIn("ERROR:", result)


if __name__ == "__main__":
    unittest.main()
