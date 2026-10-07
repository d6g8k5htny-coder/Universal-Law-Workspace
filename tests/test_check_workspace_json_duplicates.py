"""Raw-text controls for BQ-27's duplicate-member-only parsing repair.

A dictionary fixture would erase member collisions before the real CLI saw them.
These fixtures retain text, run the actual checker in a fresh process, and require
an attributable handled diagnostic rather than accepting an arbitrary exit 1.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_workspace.py"
MANIFEST = ROOT / "workspace" / "repositories.json"
GOOD_OUTPUT = "repositories=9 canonical_inputs=4 problems=0\n"
READ_FAILURE_COUNTS = "repositories=0 canonical_inputs=0 problems=1"


def manifest_with_members(members: str, replaced: tuple[str, ...] = ()) -> str:
    """Preserve supplied raw members; remove only named baseline members."""
    remainder = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key in replaced:
        del remainder[key]
    return "{" + members + "," + json.dumps(remainder)[1:]


def run_raw(raw: str, *, default_path: bool = False):
    with tempfile.TemporaryDirectory(prefix="bq27-json-") as tmp:
        root = Path(tmp)
        checker = CHECKER
        path = root / "input.json"
        if default_path:
            checker = root / "tools" / "check_workspace.py"
            checker.parent.mkdir()
            checker.write_bytes(CHECKER.read_bytes())
            path = root / "workspace" / "repositories.json"
            path.parent.mkdir()
        path.write_text(raw, encoding="utf-8")
        before = path.read_bytes()
        args = [sys.executable, "-B"]
        if sys.flags.optimize:
            args.append("-O")
        args += ["-S", str(checker)]
        if not default_path:
            args.append(str(path))
        env = dict(os.environ, PYTHONIOENCODING="utf-8:strict")
        proc = subprocess.run(args, cwd=root, env=env, capture_output=True,
                              text=True, encoding="utf-8", timeout=30,
                              check=False)
        after = path.read_bytes()
        return proc, str(path), before, after


class JSONDuplicateControls(unittest.TestCase):
    def assert_duplicate(self, raw: str, key: str, *, default_path=False):
        proc, path, before, after = run_raw(raw, default_path=default_path)
        expected = (f"problem: cannot read manifest {path}: duplicate JSON member: "
                    f"{json.dumps(key, ensure_ascii=True)}\n"
                    f"{READ_FAILURE_COUNTS}\n")
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr),
                         (1, expected, ""))
        self.assertEqual(before, after, "checker must not rewrite its input")

    def assert_positive(self, raw: str):
        proc, _, before, after = run_raw(raw)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr),
                         (0, GOOD_OUTPUT, ""))
        self.assertEqual(before, after)

    def test_canonical_manifest_explicit_and_default_path_pass(self):
        raw = MANIFEST.read_text(encoding="utf-8")
        for default in (False, True):
            with self.subTest(default=default):
                proc, _, before, after = run_raw(raw, default_path=default)
                self.assertEqual((proc.returncode, proc.stdout, proc.stderr),
                                 (0, GOOD_OUTPUT, ""))
                self.assertEqual(before, after)

    def test_conflicting_root_authority_is_rejected_in_both_orders(self):
        key = "scientific_status_authority"
        for left, right in (("true", "false"), ("false", "true")):
            with self.subTest(left=left):
                self.assert_duplicate(manifest_with_members(
                    f'"{key}":{left},"{key}":{right}', (key,)), key)

    def test_equal_valued_members_are_not_silently_coalesced(self):
        for value in ("null", "false", "0", '"same"', "[]", "{}"):
            with self.subTest(value=value):
                self.assert_duplicate(manifest_with_members(
                    f'"probe":{value},"probe":{value}'), "probe")

    def test_conflicting_source_members_are_rejected_in_both_orders(self):
        good = json.loads(MANIFEST.read_text(encoding="utf-8"))
        item = good["canonical_inputs"]["downstream_gate"]
        for key, bad in (("repository", '"outside/federation"'),
                         ("path", '"other.json"'),
                         ("observed_blob", '"bad-blob"')):
            valid = json.dumps(item[key])
            for left, right in ((bad, valid), (valid, bad)):
                with self.subTest(key=key, left=left):
                    source = dict(item)
                    del source[key]
                    raw_source = ("{" + json.dumps(key) + ":" + left + ","
                                  + json.dumps(key) + ":" + right + ","
                                  + json.dumps(source)[1:])
                    others = dict(good["canonical_inputs"])
                    del others["downstream_gate"]
                    inputs = ('{"downstream_gate":' + raw_source + ","
                              + json.dumps(others)[1:])
                    raw = manifest_with_members('"canonical_inputs":' + inputs,
                                                ("canonical_inputs",))
                    self.assert_duplicate(raw, key)

    def test_repeated_canonical_input_objects_are_rejected(self):
        good = json.loads(MANIFEST.read_text(encoding="utf-8"))
        inputs = dict(good["canonical_inputs"])
        source = json.dumps(inputs.pop("downstream_gate"))
        raw = ('{"downstream_gate":' + source + ',"downstream_gate":'
               + source + "," + json.dumps(inputs)[1:])
        self.assert_duplicate(manifest_with_members('"canonical_inputs":' + raw,
                              ("canonical_inputs",)), "downstream_gate")

    def test_repository_entry_members_are_rejected(self):
        good = json.loads(MANIFEST.read_text(encoding="utf-8"))
        repositories = good["repositories"]
        name = json.dumps(repositories[0]["full_name"])
        for left, right in ((name, '"other/name"'), ('"other/name"', name)):
            with self.subTest(left=left):
                raw = ('[{"full_name":' + left + ',"full_name":' + right
                       + "}," + json.dumps(repositories[1:])[1:])
                self.assert_duplicate(manifest_with_members('"repositories":'
                                      + raw, ("repositories",)), "full_name")

    def test_duplicates_in_nested_objects_and_arrays_are_rejected(self):
        for raw in ('{"k":1,"k":2}', '[{"k":1,"k":2}]',
                    '{"level":[{"inner":{"k":1,"k":2}}]}'):
            with self.subTest(raw=raw):
                self.assert_duplicate(manifest_with_members('"probe":' + raw),
                                      "k")

    def test_escaped_equivalent_and_unusual_names_are_rejected_safely(self):
        for first, second, key in ((r'"a"', r'"\u0061"', "a"),
                                   (r'"\u0061"', r'"a"', "a"),
                                   ('"\U0001f600"', r'"\ud83d\ude00"', "\U0001f600"),
                                   (r'"line\nkey"', r'"line\u000akey"', "line\nkey"),
                                   (r'"\ud800"', r'"\ud800"', "\ud800"),
                                   ('""', '""', "")):
            with self.subTest(key=repr(key)):
                raw = manifest_with_members(first + ":1," + second + ":2")
                self.assert_duplicate(raw, key)

    def test_repeated_names_in_distinct_objects_and_string_text_are_valid(self):
        for raw in ('{"a":{"k":1},"b":{"k":2}}',
                    '[{"k":1},{"k":2}]',
                    json.dumps('member-like text: "k":1,"k":2')):
            with self.subTest(raw=raw):
                self.assert_positive(manifest_with_members('"probe":' + raw))
        self.assert_positive(manifest_with_members('"probe":{"A":1,"a":2}'))

    def test_default_path_also_uses_duplicate_rejection(self):
        self.assert_duplicate(manifest_with_members('"probe":0,"probe":1'),
                              "probe", default_path=True)

    def test_nonduplicate_malformed_inputs_keep_their_refusal_interface(self):
        for raw in ("null", "[]", "true", '"text"', "4"):
            with self.subTest(raw=raw):
                proc, _, before, after = run_raw(raw)
                self.assertEqual((proc.returncode, proc.stdout, proc.stderr),
                                 (1, "problem: manifest root must be an object\n"
                                  + READ_FAILURE_COUNTS + "\n", ""))
                self.assertEqual(before, after)
        proc, path, before, after = run_raw("{")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(proc.stdout.startswith(f"problem: cannot read manifest {path}: "))
        self.assertNotIn("duplicate JSON member", proc.stdout)
        self.assertTrue(proc.stdout.endswith(READ_FAILURE_COUNTS + "\n"))
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
