"""Depth-0 negative controls for tools/check_workspace.py.

The AMEND review on PR #2 found that the authority boundary failed open at the
manifest root: `_walk_forbidden_keys` was handed each top-level VALUE, so a
top-level KEY such as `lemma_closed` was never tested, and a manifest carrying
`"lemma_closed": true` at `$` passed with problems=0. The existing contract test
mutates a nested key only, so it could not see this.

These controls pin the repair. Every fixture starts from the committed manifest,
so the positive control is the real tree and each negative control weakens
exactly one fact. Scientific effect: NONE — this is a checker for a manifest.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_workspace.py"
MANIFEST = ROOT / "workspace" / "repositories.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("_check_workspace_under_test", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def committed_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


class RootKeyControls(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_checker()

    def test_committed_manifest_passes(self) -> None:
        self.assertEqual(self.mod.check_manifest(committed_manifest()), [])

    def test_every_forbidden_key_is_refused_at_the_root(self) -> None:
        for key in sorted(self.mod.FORBIDDEN_STATE_KEYS):
            with self.subTest(key=key):
                data = copy.deepcopy(committed_manifest())
                data[key] = True
                problems = self.mod.check_manifest(data)
                self.assertTrue(
                    any(f"$.{key}" in p and key in p for p in problems),
                    f"top-level {key!r} was accepted: {problems}",
                )

    def test_lemma_closed_and_promotion_permission_together_are_refused(self) -> None:
        data = copy.deepcopy(committed_manifest())
        data["lemma_closed"] = True
        data["promotion_permission"] = True
        problems = self.mod.check_manifest(data)
        self.assertGreaterEqual(len(problems), 2, problems)

    def test_authority_asserted_away_from_the_checked_field_is_refused(self) -> None:
        data = copy.deepcopy(committed_manifest())
        data.setdefault("federation", {})
        if not isinstance(data["federation"], dict):
            data["federation"] = {}
        data["federation"]["scientific_status_authority"] = True
        problems = self.mod.check_manifest(data)
        self.assertTrue(
            any("authority asserted" in p for p in problems),
            f"nested scientific_status_authority=true was accepted: {problems}",
        )

    def test_authority_false_away_from_the_checked_field_is_still_refused_as_unsupported_or_passes(self) -> None:
        # A nested `scientific_status_authority: false` asserts nothing; the
        # repair must not turn a harmless false into an authority problem.
        data = copy.deepcopy(committed_manifest())
        data.setdefault("federation", {})
        if not isinstance(data["federation"], dict):
            data["federation"] = {}
        data["federation"]["scientific_status_authority"] = False
        problems = self.mod.check_manifest(data)
        self.assertFalse(
            any("authority asserted" in p for p in problems),
            f"a nested false was reported as an assertion: {problems}",
        )

    def test_nested_forbidden_key_is_still_refused(self) -> None:
        # The pre-existing behaviour the repair must not regress.
        data = copy.deepcopy(committed_manifest())
        data["repositories"][0]["classification"] = "PROVED"
        problems = self.mod.check_manifest(data)
        self.assertTrue(any("classification" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
