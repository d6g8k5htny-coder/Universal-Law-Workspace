"""Mutation self-test of the Layer A scanner (CBZ-0 gate G0, directive §2.3/A8).

Each mutant is a copy of tools/cbz/layer_a_scan.py with one deliberate defect:
a hazard token dropped, a lexer rule broken, or a fail-closed exit weakened.
The scanner's own suite (tests/test_cbz_layer_a_scan.py) is run against every
mutant through $CBZ_LAYER_A_SCAN and must FAIL. A surviving mutant means the
suite cannot tell a broken auditor from a sound one, so this test fails.

Every replacement must match the scanner source exactly once, so the harness
cannot silently drift out of sync with the code it mutates. A mutant counts as
killed only when the suite loaded and ran, and at least one test failed or
errored; a suite that could not even be imported proves nothing.
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
SCANNER = os.path.join(WORKSPACE, "tools", "cbz", "layer_a_scan.py")

MUTANTS = [
    ("drop sorry", '    "sorry": "A1",\n', ""),
    ("drop admit", '    "admit": "A1",\n', ""),
    ("drop axiom", '    "axiom": "A2",\n', ""),
    ("drop native_decide", '    "native_decide": "A2",\n', ""),
    ("drop sorryAx", '    "sorryAx": "A1",\n', ""),
    ("drop admitGoal", '    "admitGoal": "A1",\n', ""),
    ("drop mkSorry", '    "mkSorry": "A1",\n', ""),
    ("drop ofReduceBool", '    "ofReduceBool": "A2",\n', ""),
    ("drop ofReduceNat", '    "ofReduceNat": "A2",\n', ""),
    ("drop trustCompiler", '    "trustCompiler": "A2",\n', ""),
    ("drop skipKernelTC", '    "skipKernelTC": "A2",\n', ""),
    ("drop Float review", '    "Float": "A3",\n', ""),
    ("violation demoted to review", 'return name, VIOLATION_EXACT[name], "violation"',
     'return name, VIOLATION_EXACT[name], "review"'),
    ("no line comments", 'if c == "-" and text.startswith("--", i):', 'if False:'),
    ("flat block comments", "                    depth += 1\n", "                    depth = 1\n"),
    ("plain strings not skipped", "        if c == '\"':\n            advance(1)\n            while i < n:",
     "        if False:\n            advance(1)\n            while i < n:"),
    ("interpolation regions not lexed", 'stack.append(["code", 0])', "pass"),
    ("char literals not recognised", "m = _CHAR_LIT.match(text, i)", "m = None"),
    ("raw strings not recognised", 'if word == "r" and i < n', 'if False and i < n'),
    ("dotted names not split", 'last = name.split(".")[-1]', "last = name"),
    ("stop flagged anywhere", "if line_start and name in LINE_START_REVIEW:",
     "if name in LINE_START_REVIEW:"),
    ("evidence treated as production", 'return "evidence_copy"', 'return "production"'),
    ("git mode lists no blobs", 'if typ == b"blob" and p.endswith(".lean"):', "if False:"),
    ("violations never fail", "return 1 if failing else 0", "return 0"),
    ("undecodable files pass", "    if undecodable:\n        return 1\n",
     "    if False:\n        return 1\n"),
    ("fail on every context by default", 'ap.add_argument("--fail-on", default="production")',
     'ap.add_argument("--fail-on", default="all")'),
]


def run_suite(scanner_path):
    env = dict(os.environ, CBZ_LAYER_A_SCAN=scanner_path, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_cbz_layer_a_scan"],
                          cwd=WORKSPACE, env=env, capture_output=True, text=True, timeout=600)


def killed(r):
    out = r.stdout + r.stderr
    return (r.returncode != 0 and re.search(r"^Ran [1-9][0-9]* tests?", out, re.M) is not None
            and "FAILED (" in out and "Failed to import test module" not in out)


class ScannerMutants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCANNER, encoding="utf-8") as fh:
            cls.source = fh.read()

    def test_unmutated_scanner_passes_its_suite(self):
        r = run_suite(SCANNER)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_mutant_is_killed(self):
        survivors = []
        with tempfile.TemporaryDirectory() as d:
            for i, (name, old, new) in enumerate(MUTANTS):
                with self.subTest(mutant=name):
                    self.assertEqual(self.source.count(old), 1, f"mutation point drifted: {name}")
                    path = os.path.join(d, f"mutant_{i:02d}.py")
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(self.source.replace(old, new))
                    r = run_suite(path)
                    if not killed(r):
                        survivors.append(name)
        self.assertEqual(survivors, [], f"surviving mutants: {survivors}")
        self.assertGreaterEqual(len(MUTANTS), 26)


if __name__ == "__main__":
    unittest.main()
