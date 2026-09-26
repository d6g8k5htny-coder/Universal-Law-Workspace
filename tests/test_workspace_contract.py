import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_workspace.py"
MANIFEST = ROOT / "workspace" / "repositories.json"


def run_checker(data):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "repositories.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )


class WorkspaceContractTests(unittest.TestCase):
    def setUp(self):
        self.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_committed_manifest_passes_and_does_not_duplicate_role_registry(self):
        for item in self.good["repositories"]:
            self.assertEqual(
                set(item),
                {"full_name"},
                "machine repository-role metadata belongs only in "
                "meta-framework/registry.json",
            )
        result = run_checker(self.good)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("problems=0", result.stdout)

    def test_status_authority_must_stay_false(self):
        data = json.loads(json.dumps(self.good))
        data["scientific_status_authority"] = True
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scientific_status_authority must be false", result.stdout)

    def test_forbidden_status_field_is_rejected_anywhere(self):
        data = json.loads(json.dumps(self.good))
        data["repositories"][0]["classification"] = "PROVED_REVIEWED"
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden scientific-state key", result.stdout)

    def test_duplicate_repository_is_rejected(self):
        data = json.loads(json.dumps(self.good))
        data["repositories"].append(dict(data["repositories"][0]))
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate repository", result.stdout)

    def test_required_repository_cannot_disappear(self):
        data = json.loads(json.dumps(self.good))
        data["repositories"] = [
            item
            for item in data["repositories"]
            if item["full_name"] != "d6g8k5htny-coder/Math-"
        ]
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required repository", result.stdout)

    def test_canonical_input_requires_observed_blob(self):
        data = json.loads(json.dumps(self.good))
        del data["canonical_inputs"]["downstream_gate"]["observed_blob"]
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observed_blob", result.stdout)

    def test_repository_role_metadata_is_rejected(self):
        data = json.loads(json.dumps(self.good))
        for item in data["repositories"]:
            item.pop("role", None)
        data["repositories"][0]["role"] = "Duplicate machine role"
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "repository role metadata belongs to repository_registry",
            result.stdout,
        )

    def test_canonical_input_repository_must_be_in_federation(self):
        data = json.loads(json.dumps(self.good))
        data["canonical_inputs"]["downstream_gate"]["repository"] = (
            "d6g8k5htny-coder/not-in-federation"
        )
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "canonical input downstream_gate repository is not in federation",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
