"""Mutation controls for canonical source identity verification."""
import os
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


def intended_failure(result, test):
    output = result.stdout + result.stderr
    return (result.returncode != 0 and "FAILED (failures=1)" in output
            and "ERROR:" not in output
            and output.count("Traceback (most recent call last)") == 1)


class CanonicalHarnessControls(unittest.TestCase):
    def test_actual_silent_checker_exit_is_not_a_mutation_kill(self):
        flags = ["-B"] + (["-O"] if sys.flags.optimize else [])
        with tempfile.TemporaryDirectory(prefix="canonical-silent-crash-") as folder:
            checker = Path(folder) / "verify_canonical_inputs.py"
            checker.write_text("raise SystemExit(86)\n")
            env = dict(os.environ, CBZ_CANONICAL_CHECKER=str(checker))
            process = subprocess.run(
                [sys.executable, *flags, str(CONTROLS),
                 "CanonicalInputControls.test_wrong_current_blob_fails", "-q"],
                env=env, text=True, capture_output=True)
        self.assertFalse(intended_failure(process, "test_wrong_current_blob_fails"),
                         "silent checker crash was incorrectly counted as a killed mutant")


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
                    result = subprocess.run(
                        [sys.executable, *flags, str(CONTROLS),
                         "CanonicalInputControls." + test, "-q"],
                        env=env, text=True, capture_output=True)
                    output = result.stdout + result.stderr
                    self.assertTrue(intended_failure(result, test),
                                    "not an intended kill: " + label + "\n" + output)


if __name__ == "__main__":
    unittest.main()
