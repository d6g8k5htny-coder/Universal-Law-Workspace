"""Unit and negative controls for tools/cbz/layer_a_scan.py (CBZ-0 gate G0/G1).

The scanner under test is loaded from $CBZ_LAYER_A_SCAN when set (the mutation
harness in test_cbz_layer_a_scan_mutants.py points it at mutated copies), else
from tools/cbz/layer_a_scan.py. Every case asserts the exact finding list, so a
scanner that over- or under-reports fails.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
SCANNER = os.environ.get("CBZ_LAYER_A_SCAN") or os.path.join(WORKSPACE, "tools", "cbz", "layer_a_scan.py")


def _load():
    spec = importlib.util.spec_from_file_location("layer_a_scan_under_test", SCANNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load()


def hits(text, path="Pkg/Mod.lean"):
    return [(f["line"], f["col"], f["kind"], f["severity"]) for f in M.scan_text(text, path)]


def cli(args, cwd=None):
    return subprocess.run([sys.executable, "-I", SCANNER] + list(args), cwd=cwd,
                          capture_output=True, text=True)


class ViolationTokens(unittest.TestCase):
    def test_each_violation_token_detected(self):
        cases = {
            "theorem t : True := by sorry": [(1, 24, "sorry", "violation")],
            "theorem t : True := sorry": [(1, 21, "sorry", "violation")],
            "example : True := by\n  admit": [(2, 3, "admit", "violation")],
            "axiom bad : False": [(1, 1, "axiom", "violation")],
            "private axiom bad : False": [(1, 9, "axiom", "violation")],
            "theorem t : 2 = 2 := by native_decide": [(1, 25, "native_decide", "violation")],
            "def x := Lean.ofReduceBool": [(1, 10, "ofReduceBool", "violation")],
            "def x := Lean.ofReduceNat": [(1, 10, "ofReduceNat", "violation")],
            "def x := Lean.trustCompiler": [(1, 10, "trustCompiler", "violation")],
            "set_option debug.skipKernelTC true": [(1, 12, "skipKernelTC", "violation")],
            "def x := mkConst ``sorryAx": [(1, 20, "sorryAx", "violation")],
            "def x := Lean.Elab.admitGoal": [(1, 10, "admitGoal", "violation")],
            "def x := Lean.Meta.mkSorry": [(1, 10, "mkSorry", "violation")],
        }
        for src, want in cases.items():
            with self.subTest(src=src):
                self.assertEqual(hits(src), want)

    def test_review_tokens(self):
        self.assertEqual(hits("def f (x : Float) := x"), [(1, 12, "Float", "review")])
        self.assertEqual(hits("def f (x : Float32) := x"), [(1, 12, "Float32", "review")])
        self.assertEqual(hits("unsafe def f := 1"), [(1, 1, "unsafe", "review")])
        self.assertEqual(hits("@[implemented_by g] def f := 1"), [(1, 3, "implemented_by", "review")])
        self.assertEqual(hits("@[extern \"c\"] def f := 1"), [(1, 3, "extern", "review")])
        self.assertEqual(hits("example : True := by\n  stop\n  trivial"), [(2, 3, "stop", "review")])

    def test_stop_only_at_line_start(self):
        self.assertEqual(hits("def stop := 1"), [])
        self.assertEqual(hits("example := f stop"), [])

    def test_multiple_and_positions(self):
        src = "theorem a : True := sorry\n\ntheorem b : True := by\n    admit\naxiom c : False\n"
        self.assertEqual(hits(src), [(1, 21, "sorry", "violation"), (4, 5, "admit", "violation"),
                                     (5, 1, "axiom", "violation")])

    def test_eof_without_newline(self):
        self.assertEqual(hits("example : True := sorry"), [(1, 19, "sorry", "violation")])

    def test_unicode_before_token_counts_characters(self):
        self.assertEqual(hits("theorem α₁ : True := sorry"), [(1, 22, "sorry", "violation")])


class NotCode(unittest.TestCase):
    def test_line_comment(self):
        self.assertEqual(hits("-- sorry admit axiom native_decide\ntheorem t : True := trivial"), [])
        self.assertEqual(hits("theorem t : True := trivial -- sorry"), [])

    def test_block_comments_nested_and_doc(self):
        self.assertEqual(hits("/- sorry /- nested sorry -/ still sorry -/ def x := 1"), [])
        self.assertEqual(hits("/-- doc: uses sorry -/ def x := 1"), [])
        self.assertEqual(hits("/-! module doc axiom -/"), [])
        # a single close of a two-deep nest must not end the comment
        self.assertEqual(hits("/- a /- b -/ sorry -/ def y := sorry"), [(1, 32, "sorry", "violation")])

    def test_strings(self):
        self.assertEqual(hits('def s := "sorry axiom"'), [])
        self.assertEqual(hits('def s := "escaped \\" sorry"'), [])
        self.assertEqual(hits('def s := "a\\\\" ; theorem t : True := sorry'),
                         [(1, 38, "sorry", "violation")])
        self.assertEqual(hits('def s := "-- not a comment" ; def t := sorry'),
                         [(1, 40, "sorry", "violation")])
        self.assertEqual(hits('def s := "/- not a comment" ; def t := sorry'),
                         [(1, 40, "sorry", "violation")])

    def test_raw_strings(self):
        self.assertEqual(hits('def s := r"sorry"'), [])
        self.assertEqual(hits('def s := r#"a " sorry "#'), [])
        self.assertEqual(hits('def s := r#"a " x "# ; def t := sorry'), [(1, 33, "sorry", "violation")])

    def test_char_literals_do_not_open_strings(self):
        self.assertEqual(hits("def q := '\"' ; theorem t : True := sorry"),
                         [(1, 36, "sorry", "violation")])
        self.assertEqual(hits("def q := '\\'' ; theorem t : True := sorry"),
                         [(1, 37, "sorry", "violation")])
        self.assertEqual(hits("def f' := 1 ; def g'' := f' ; def h := sorry"),
                         [(1, 40, "sorry", "violation")])

    def test_interpolated_strings(self):
        self.assertEqual(hits('def s := s!"{1} sorry"'), [])
        self.assertEqual(hits('def s := s!"x {sorry} y"'), [(1, 16, "sorry", "violation")])
        self.assertEqual(hits('def s := s!"x {f "sorry" sorry} y"'), [(1, 26, "sorry", "violation")])
        self.assertEqual(hits('def s := m!"{ {a := 1} } sorry" ; def t := sorry'),
                         [(1, 44, "sorry", "violation")])

    def test_identifiers_containing_keywords(self):
        self.assertEqual(hits("def sorryFree := mysorry ; def admitted := axiomatic"), [])
        self.assertEqual(hits("def native_decide_ok := 1 ; def Floaty := 2"), [])
        self.assertEqual(hits("#print axioms foo"), [])
        self.assertEqual(hits("def x := Foo.sorry ; def y := Bar.axiom"), [])

    def test_escaped_identifiers(self):
        self.assertEqual(hits("def «sorry» := 1 ; def x := «axiom»"), [])
        self.assertEqual(hits("def x := Lean.«ofReduceBool»"), [])


class Context(unittest.TestCase):
    def test_context_classification(self):
        self.assertEqual(M.context_of("frontiers/x/Mod.lean"), "production")
        self.assertEqual(M.context_of("frontiers/x/foo-evidence/raw/producer/runs/a/Mod.lean"), "evidence_copy")
        self.assertEqual(M.context_of("a/raw/Mod.lean"), "evidence_copy")
        self.assertEqual(M.context_of("frontiers/x/ModControls.lean"), "control")
        self.assertEqual(M.context_of("frontiers/x/NegativeSorry.lean"), "control")
        self.assertEqual(M.scan_text("def t := sorry", "a/raw/M.lean")[0]["context"], "evidence_copy")


class CommandLine(unittest.TestCase):
    def write(self, d, rel, text, raw=None):
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(raw if raw is not None else text.encode("utf-8"))
        return p

    def test_clean_tree_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "A.lean", "theorem t : True := trivial -- sorry\n")
            r = cli([d])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1])["violations"], 0)

    def test_production_violation_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "A.lean", "theorem t : True := sorry\n")
            r = cli([d])
            self.assertEqual(r.returncode, 1)
            self.assertIn("A.lean:1:21: A1 sorry (production)", r.stdout)

    def test_evidence_violation_reported_not_failing_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "x-evidence/raw/A.lean", "theorem t : True := sorry\n")
            out = os.path.join(d, "out.json")
            r = cli([d, "--json", out])
            self.assertEqual(r.returncode, 0, r.stdout)
            with open(out, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["summary"]["violations"], 1)
            self.assertEqual(data["findings"][0]["context"], "evidence_copy")
            r2 = cli([d, "--fail-on", "all"])
            self.assertEqual(r2.returncode, 1)

    def test_review_only_does_not_fail(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "A.lean", "def f (x : Float) := x\n")
            self.assertEqual(cli([d]).returncode, 0)

    def test_undecodable_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "A.lean", None, raw=b"theorem t : True := \xff\xfe\n")
            r = cli([d])
            self.assertEqual(r.returncode, 1)
            self.assertIn("undecodable", r.stdout)

    def test_non_lean_files_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "A.md", "sorry\n")
            r = cli([d])
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout.strip().splitlines()[-1])["files"], 0)

    def test_usage_error(self):
        self.assertEqual(cli([]).returncode, 2)

    def test_git_tree_mode(self):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
            run = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x",
                                             "-c", "commit.gpgsign=false"] + list(a), cwd=d,
                                            check=True, capture_output=True, env=env)
            run("init", "-q")
            self.write(d, "src/A.lean", "theorem t : True := sorry\n")
            self.write(d, "src/B.lean", "theorem u : True := trivial\n")
            run("add", "-A")
            run("commit", "-q", "-m", "c")
            # the working tree is changed afterwards; git mode must read the commit
            self.write(d, "src/A.lean", "theorem t : True := trivial\n")
            out = os.path.join(d, "o.json")
            r = cli(["--git", d, "--rev", "HEAD", "--json", out])
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            with open(out, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["summary"]["files"], 2)
            self.assertEqual([(f["path"], f["kind"]) for f in data["findings"]], [("src/A.lean", "sorry")])
            self.assertEqual(len(data["findings"][0]["blob"]), 40)


if __name__ == "__main__":
    unittest.main()
