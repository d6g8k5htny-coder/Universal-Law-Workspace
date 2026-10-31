#!/usr/bin/env python3
"""Layer A3 float-use census for Python sources (CBZ-0 Phase 1 discovery).

Layer A3 forbids floating-point certification of mathematical bounds. Whether a
given float is *used to certify* a bound is a question about intent that no
static tool can settle, so this tool is a census, not a certifier: it records,
for every Python file, exactly where floating-point arithmetic can enter, plus
the exact-arithmetic machinery the file uses, so each file can be triaged.

Signals (each reported with line and column):
  float_literal     a float or complex literal (``0.5``, ``1e-9``, ``2j``)
  float_call        a call ``float(...)`` or ``complex(...)``
  true_division     the ``/`` or ``/=`` operator (int / int yields a float)
  math_float        ``math.X`` / ``cmath.X`` for any X not in EXACT_MATH
                    (attribute access or ``from math import X``)
  float_module      import of numpy, scipy, mpmath, decimal or cmath
  exact_module      import of fractions, sympy, flint (python-flint) or
                    gmpy2, or use of ``mpmath.iv`` (interval arithmetic)
  interval_layer    an outward-rounding interval layer: ``math.nextafter`` /
                    ``math.ulp`` (attribute or import), or an import of a
                    module named ``ia`` (the project's outward-rounded
                    interval modules), including ``from pkg import ia``

Classification per file (derived only from the signals above):
  NO_FLOAT_SIGNAL    no float_literal / float_call / true_division /
                     math_float / float_module
  FLOAT_SIGNAL       at least one of those, and no exact_module
  MIXED              float signals and exact or interval machinery both present
  UNPARSEABLE        the file is not valid Python 3 (fails closed)

Module aliases (``import math as m``) are collected from the whole file
before any expression is classified, so a function body that uses an alias
imported later is still counted. Sources are parsed from bytes, honouring a
UTF-8 BOM and PEP 263 encoding declarations.

Standard library only; no floating point is used in any decision. The exit
status is 0 when every file parsed and 1 when any file is UNPARSEABLE; signal
counts never change the exit status, because they are inventory, not verdicts.
A missing input path or an untraversable directory is an IO error (exit 2).

Usage:
  a3_float_census.py PATH...                 directories and/or .py files
  a3_float_census.py --git REPO --rev REV    every .py blob in a git tree
  --json FILE                                write the full census
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys

# math functions that return ints (or bools) exactly for int arguments.
# fabs, copysign, sqrt, exp, log, pi, e, ... return floats and are NOT here.
EXACT_MATH = {
    "comb", "factorial", "gcd", "isqrt", "lcm", "perm", "prod",
    "floor", "ceil", "trunc", "isfinite", "isinf", "isnan",
}
FLOAT_MODULES = {"numpy", "scipy", "mpmath", "decimal", "cmath"}
EXACT_MODULES = {"fractions", "sympy", "flint", "gmpy2"}
FLOAT_KINDS = ("float_literal", "float_call", "true_division", "math_float", "float_module")
INTERVAL_MATH = {"nextafter", "ulp"}


class _Visitor(ast.NodeVisitor):
    def __init__(self):
        self.signals: list[tuple[int, int, str, str]] = []
        self.math_aliases = {"math": "math", "cmath": "cmath"}
        self.mpmath_aliases = {"mpmath"}
        self.local_math_names: dict[str, str] = {}

    def collect_aliases(self, tree):
        # first pass: module aliases are visible to code that precedes the import
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    top = a.name.split(".")[0]
                    bound = (a.asname or a.name).split(".")[0]
                    if top in ("math", "cmath"):
                        self.math_aliases[bound] = top
                    if top == "mpmath":
                        self.mpmath_aliases.add(bound)

    def add(self, node, kind, detail):
        self.signals.append((getattr(node, "lineno", 0), getattr(node, "col_offset", -1) + 1, kind, detail))

    # -- imports
    def visit_Import(self, node):
        for a in node.names:
            top = a.name.split(".")[0]
            bound = (a.asname or a.name).split(".")[0]
            if top in ("math", "cmath"):
                self.math_aliases[bound] = top
            if top == "mpmath":
                self.mpmath_aliases.add(bound)
            if a.name == "ia" or a.name.endswith(".ia"):
                self.add(node, "interval_layer", f"import {a.name}")
            self._module(node, a.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        top = mod.split(".")[0]
        self._module(node, mod)
        if mod == "ia" or mod.endswith(".ia"):
            self.add(node, "interval_layer", f"from {mod} import")
        elif any(a.name == "ia" for a in node.names):
            self.add(node, "interval_layer", f"from {'.' * node.level}{mod} import ia")
        if top in ("math", "cmath"):
            for a in node.names:
                if a.name not in EXACT_MATH:
                    self.add(node, "math_float", f"from {mod} import {a.name}")
                if a.name in INTERVAL_MATH:
                    self.add(node, "interval_layer", f"{top}.{a.name}")
                self.local_math_names[a.asname or a.name] = top
        if top == "mpmath":
            for a in node.names:
                if a.name == "iv":
                    self.add(node, "exact_module", "mpmath.iv")
        self.generic_visit(node)

    def _module(self, node, name):
        top = name.split(".")[0]
        if name == "mpmath.iv":
            self.add(node, "exact_module", "mpmath.iv")
        if top in FLOAT_MODULES:
            self.add(node, "float_module", top)
        if top in EXACT_MODULES:
            self.add(node, "exact_module", top)

    # -- expressions
    def visit_Constant(self, node):
        if isinstance(node.value, (float, complex)) and not isinstance(node.value, bool):
            self.add(node, "float_literal", repr(node.value))

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ("float", "complex"):
            self.add(node, "float_call", node.func.id)
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Div):
            self.add(node, "true_division", "/")
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.op, ast.Div):
            self.add(node, "true_division", "/=")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            base = node.value.id
            if base in self.math_aliases and node.attr not in EXACT_MATH:
                self.add(node, "math_float", f"{self.math_aliases[base]}.{node.attr}")
            if base in self.math_aliases and node.attr in INTERVAL_MATH:
                self.add(node, "interval_layer", f"{self.math_aliases[base]}.{node.attr}")
            if base in self.mpmath_aliases and node.attr == "iv":
                self.add(node, "exact_module", "mpmath.iv")
        self.generic_visit(node)


def census_text(text: str | bytes, path: str, blob: str | None = None) -> dict:
    """Census one source; bytes are decoded as Python would (BOM, encoding cookie)."""
    rec = {"path": path}
    if blob:
        rec["blob"] = blob
    try:
        tree = ast.parse(text, filename=path)
    except (SyntaxError, ValueError, LookupError) as exc:
        rec.update({"class": "UNPARSEABLE", "error": f"{type(exc).__name__}: {exc}", "signals": [], "counts": {}})
        return rec
    v = _Visitor()
    v.collect_aliases(tree)
    v.visit(tree)
    sig = sorted(v.signals)
    counts: dict[str, int] = {}
    for _, _, kind, _ in sig:
        counts[kind] = counts.get(kind, 0) + 1
    has_float = any(counts.get(k) for k in FLOAT_KINDS)
    has_exact = bool(counts.get("exact_module") or counts.get("interval_layer"))
    cls = "NO_FLOAT_SIGNAL" if not has_float else ("MIXED" if has_exact else "FLOAT_SIGNAL")
    rec.update({"class": cls, "counts": counts,
                "signals": [{"line": l, "col": c, "kind": k, "detail": d} for l, c, k, d in sig]})
    return rec


def _raise(exc):
    raise exc


def _iter_fs(paths):
    for p in paths:
        if not os.path.exists(p):
            raise FileNotFoundError(2, "input path does not exist", p)
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p, onerror=_raise):
                dirs[:] = sorted(d for d in dirs if d != ".git")
                for fn in sorted(files):
                    if fn.endswith(".py"):
                        full = os.path.join(root, fn)
                        yield os.path.relpath(full, p), full
        elif p.endswith(".py"):
            yield p, p


def _git_blobs(repo, rev):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    ls = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", rev],
                        check=True, capture_output=True, env=env).stdout
    entries = []
    for rec in ls.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        _mode, typ, sha = meta.split()
        p = path.decode("utf-8", "surrogateescape")
        if typ == b"blob" and p.endswith(".py"):
            entries.append((p, sha.decode()))
    if not entries:
        return
    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    try:
        for p, sha in entries:
            proc.stdin.write(sha.encode() + b"\n")
            proc.stdin.flush()
            size = int(proc.stdout.readline().split()[2])
            data = proc.stdout.read(size)
            proc.stdout.read(1)
            yield p, sha, data
    finally:
        proc.stdin.close()
        proc.wait()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--git", metavar="REPO")
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--json", metavar="FILE")
    args = ap.parse_args(argv)
    if not args.paths and not args.git:
        ap.print_usage(sys.stderr)
        return 2
    records = []
    try:
        if args.git:
            for p, sha, data in _git_blobs(args.git, args.rev):
                records.append(census_text(data, p, sha))
        for rel, full in _iter_fs(args.paths):
            with open(full, "rb") as fh:
                data = fh.read()
            records.append(census_text(data, rel))
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"a3_float_census: error: {exc}", file=sys.stderr)
        return 2
    by_class: dict[str, int] = {}
    for r in records:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    summary = {"files": len(records), "by_class": dict(sorted(by_class.items()))}
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "files": records}, fh, indent=1, ensure_ascii=False)
    for r in records:
        if r["class"] == "UNPARSEABLE":
            print(f"{r['path']}: UNPARSEABLE {r['error']}")
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if by_class.get("UNPARSEABLE") else 0


if __name__ == "__main__":
    sys.exit(main())
