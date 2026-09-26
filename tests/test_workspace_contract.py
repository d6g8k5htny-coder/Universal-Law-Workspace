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

    def test_committed_manifest_passes(self):
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

    def test_workspace_role_must_explicitly_say_federation(self):
        data = json.loads(json.dumps(self.good))
        data["repositories"][0]["role"] = "Generic repository"
        result = run_checker(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("workspace role must contain 'Federation'", result.stdout)


if __name__ == "__main__":
    unittest.main()
