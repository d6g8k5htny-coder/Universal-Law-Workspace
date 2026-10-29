#!/usr/bin/env python3
"""Layer A textual scanner for Lean 4 sources (CBZ-0 gate G1).

What it certifies, exactly:
  For every scanned ``.lean`` file it reports each *code* token (outside
  comments, string literals and char literals) that names a Layer A hazard:

  violation tokens (gate-failing in production context)
    A1 placeholders : sorry, admit, sorryAx, admitGoal, mkSorry
    A2 trust holes  : axiom (declaration keyword), native_decide,
                      ofReduceBool, ofReduceNat, trustCompiler,
                      skipKernelTC (kernel-check bypass option),
                      addDeclWithoutChecking, and the ``decide`` options
                      ``+native`` / ``native := true``
  review tokens (reported, never gate-failing on their own)
    A3 float        : Float, Float32
    A2 compiled code: unsafe, implemented_by, extern
    A1 tactic stop  : ``stop`` as the first token on its line

  ``sorry``/``admit``/``axiom``/``native_decide``/``Float``/``Float32``/
  ``unsafe``/``stop`` match only as a whole undotted identifier; the other
  violation tokens also match as the last component of a dotted name
  (``Lean.ofReduceBool``, ``debug.skipKernelTC``), including an escaped
  component (``Lean.«ofReduceBool»`` and ``«sorryAx»`` name the same
  constants). An escaped keyword such as ``«sorry»`` is an ordinary
  identifier, not the keyword, and is not flagged.

Fail-closed: a string, block comment, raw string, interpolated string or
``«`` name left unterminated at end of file is reported as an ``error``
finding, which fails the run like a violation, because the rest of the
file cannot be lexed reliably.

What it does NOT certify:
  * That a file compiles, or that no placeholder arises through
    metaprogramming that never spells a listed token. Gates G2-G4
    (``#print axioms`` / kernel re-check) close that gap; this scanner is a
    necessary, not sufficient, condition.
  * Anything about non-Lean files (Python bounds are a separate gate).

Lexing follows Lean 4: ``--`` line comments; nested ``/- -/`` block comments
(including ``/--`` and ``/-!``); ``"..."`` strings with backslash escapes;
interpolated strings (``s!"..{code}.."``, ``m!``, ``f!``) whose ``{}``
regions are lexed as code; raw strings ``r"..."`` / ``r#"..."#``; char
literals; and ``«...»`` escaped identifiers.

Standard library only. No floating point is used in any decision.

Usage:
  layer_a_scan.py PATH...                  scan files/directories
  layer_a_scan.py --git REPO --rev REV     scan every .lean blob in a git tree
Options:
  --json FILE     write all findings as JSON
  --fail-on CTX   comma list of contexts whose violations fail the run
                  (default: production). Use "all" for every context.
Exit status: 0 = no failing violation, 1 = failing violation, 2 = usage/IO.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata

VIOLATION_EXACT = {
    "sorry": "A1",
    "admit": "A1",
    "axiom": "A2",
    "native_decide": "A2",
}
VIOLATION_COMPONENT = {
    "sorryAx": "A1",
    "admitGoal": "A1",
    "mkSorry": "A1",
    "ofReduceBool": "A2",
    "ofReduceNat": "A2",
    "trustCompiler": "A2",
    "skipKernelTC": "A2",
    "addDeclWithoutChecking": "A2",
}
REVIEW_EXACT = {
    "Float": "A3",
    "Float32": "A3",
    "unsafe": "A2",
}
REVIEW_COMPONENT = {
    "implemented_by": "A2",
    "extern": "A2",
}
LINE_START_REVIEW = {"stop": "A1"}

INTERP_PREFIXES = {"s!", "m!", "f!"}
# ``decide +native`` and ``native := true`` select compiler evaluation, i.e.
# ofReduceBool. ``native`` after a ``+`` is flagged even with a space between
# (safe direction: ``x + native`` is a false positive, never a miss).
_NATIVE_TRUE = re.compile(r"\s*:=\s*true(?![A-Za-z0-9_'!?])")
_EXCLUDED_LETTERS = {"λ", "Π", "Σ"}
_CHAR_LIT = re.compile(r"'(?:\\(?:u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^\\'\n])'")


def _is_letter(ch: str) -> bool:
    if ch in _EXCLUDED_LETTERS:
        return False
    if ch.isascii():
        return ch.isalpha()
    cat = unicodedata.category(ch)
    if cat.startswith("L"):
        return True
    o = ord(ch)
    # Letter-like symbols and Greek/Coptic, as Lean's isLetterLike.
    return (0x3B1 <= o <= 0x3C9 and o != 0x3BB) or (0x391 <= o <= 0x3A9 and o not in (0x3A0, 0x3A3)) \
        or 0x3CA <= o <= 0x3FB or 0x1F00 <= o <= 0x1FFE or 0x2100 <= o <= 0x214F \
        or 0x1D49C <= o <= 0x1D59F


def _is_subscript(ch: str) -> bool:
    o = ord(ch)
    return 0x2080 <= o <= 0x2089 or 0x2090 <= o <= 0x209C or 0x1D62 <= o <= 0x1D6A


def _id_start(ch: str) -> bool:
    return ch == "_" or _is_letter(ch)


def _id_rest(ch: str) -> bool:
    return ch == "_" or ch == "'" or ch == "!" or ch == "?" or ch.isdigit() \
        or _is_letter(ch) or _is_subscript(ch)


def lex_tokens(text: str, errors: list | None = None):
    """Yield (name, line, col, line_start, plus_before, follow) per code identifier.

    ``name`` is the full dotted identifier text; an escaped ``«...»``
    component becomes ``\x00`` plus its text (inner dots as ``\x01``), so it
    matches constant names but never a keyword. ``plus_before`` says the
    identifier follows a ``+`` on its line; ``follow`` is the text after it.
    Unterminated constructs are appended to ``errors`` as (line, col, kind).

    Modes are kept on an explicit stack: a ``code`` frame (with a brace
    depth when it is an interpolation region) or an ``istr`` frame (the body
    of an interpolated string, where ``{`` opens a nested code region).
    """
    i = 0
    n = len(text)
    line = 1
    col = 1
    line_has_token = False
    stack: list[list] = [["code", None]]
    if errors is None:
        errors = []

    def advance(k: int):
        nonlocal i, line, col, line_has_token
        for _ in range(k):
            if i >= n:
                return
            if text[i] == "\n":
                line += 1
                col = 1
                line_has_token = False
            else:
                col += 1
            i += 1

    def read_ident_tail(parts: list[str]):
        # dotted continuation: .ident or .«escaped»
        while i < n and text[i] == "." and i + 1 < n and (_id_start(text[i + 1]) or text[i + 1] == "«"):
            advance(1)
            if text[i] == "«":
                j = text.find("»", i + 1)
                if j < 0:
                    errors.append((line, col, "unterminated_escaped_name"))
                    advance(n - i)
                    return
                inner = text[i + 1:j]
                advance(j + 1 - i)
                parts.append("\x00" + inner.replace(".", "\x01"))
            else:
                s2 = i
                while i < n and _id_rest(text[i]):
                    advance(1)
                parts.append(text[s2:i])

    while i < n:
        frame = stack[-1]
        c = text[i]
        if frame[0] == "istr":
            if c == "\\":
                advance(2)
            elif c == '"':
                advance(1)
                stack.pop()
            elif c == "{":
                advance(1)
                stack.append(["code", 0])
            else:
                advance(1)
            continue
        # ---- code mode
        if c == "-" and text.startswith("--", i):
            while i < n and text[i] != "\n":
                advance(1)
            continue
        if c == "/" and text.startswith("/-", i):
            start = (line, col)
            depth = 0
            while i < n:
                if text.startswith("/-", i):
                    depth += 1
                    advance(2)
                elif text.startswith("-/", i):
                    depth -= 1
                    advance(2)
                    if depth == 0:
                        break
                else:
                    advance(1)
            if depth:
                errors.append(start + ("unterminated_comment",))
            continue
        if frame[1] is not None and c == "{":
            frame[1] += 1
            advance(1)
            continue
        if frame[1] is not None and c == "}":
            advance(1)
            if frame[1] == 0:
                stack.pop()          # back to the interpolated string body
            else:
                frame[1] -= 1
            continue
        if c == '"':
            start = (line, col)
            advance(1)
            closed = False
            while i < n:
                cc = text[i]
                if cc == "\\":
                    advance(2)
                    continue
                advance(1)
                if cc == '"':
                    closed = True
                    break
            if not closed:
                errors.append(start + ("unterminated_string",))
            line_has_token = True
            continue
        if c == "'":
            m = _CHAR_LIT.match(text, i)
            advance(m.end() - i if m else 1)
            line_has_token = True
            continue
        if c == "«":
            start_line, start_col, start_first = line, col, not line_has_token
            j = text.find("»", i + 1)
            if j < 0:
                errors.append((line, col, "unterminated_escaped_name"))
                advance(n - i)
                break
            inner = text[i + 1:j]
            advance(j + 1 - i)
            parts = ["\x00" + inner.replace(".", "\x01")]
            read_ident_tail(parts)
            line_has_token = True
            yield ".".join(parts), start_line, start_col, start_first, False, text[i:i + 40]
            continue
        if _id_start(c):
            start_line, start_col, start_first = line, col, not line_has_token
            s = i
            while i < n and _id_rest(text[i]):
                advance(1)
            word = text[s:i]
            if word == "r" and i < n and text[i] in '"#':
                k = i
                while k < n and text[k] == "#":
                    k += 1
                if k < n and text[k] == '"':
                    close = '"' + "#" * (k - i)
                    end = text.find(close, k + 1)
                    if end < 0:
                        errors.append((start_line, start_col, "unterminated_raw_string"))
                    end = n if end < 0 else end + len(close)
                    advance(end - i)
                    line_has_token = True
                    continue
            if word in INTERP_PREFIXES and i < n and text[i] == '"':
                advance(1)
                stack.append(["istr", start_line, start_col])
                line_has_token = True
                continue
            parts = [word]
            read_ident_tail(parts)
            line_has_token = True
            k = s - 1
            while k >= 0 and text[k] in " \t":
                k -= 1
            yield ".".join(parts), start_line, start_col, start_first, k >= 0 and text[k] == "+", text[i:i + 40]
            continue
        if c.isdigit():
            while i < n and (text[i].isalnum() or text[i] in "._"):
                advance(1)
            line_has_token = True
            continue
        if not c.isspace():
            line_has_token = True
        advance(1)
    for frame in stack:
        if frame[0] == "istr":
            errors.append((frame[1], frame[2], "unterminated_interpolated_string"))
            break


def classify_token(name: str, line_start: bool, plus_before: bool = False, follow: str = ""):
    """Return (kind, layer, severity) or None."""
    last = name.split(".")[-1]
    if last.startswith("\x00"):
        # escaped component: the same constant name, never a keyword
        last = last[1:]
        if last in VIOLATION_COMPONENT:
            return last, VIOLATION_COMPONENT[last], "violation"
        if last in REVIEW_COMPONENT:
            return last, REVIEW_COMPONENT[last], "review"
        return None
    if name == "native" and (plus_before or _NATIVE_TRUE.match(follow)):
        return "native", "A2", "violation"
    if "." not in name:
        if name in VIOLATION_EXACT:
            return name, VIOLATION_EXACT[name], "violation"
        if name in REVIEW_EXACT:
            return name, REVIEW_EXACT[name], "review"
        if line_start and name in LINE_START_REVIEW:
            return name, LINE_START_REVIEW[name], "review"
    if last in VIOLATION_COMPONENT:
        return last, VIOLATION_COMPONENT[last], "violation"
    if last in REVIEW_COMPONENT:
        return last, REVIEW_COMPONENT[last], "review"
    return None


_EVIDENCE_SEG = re.compile(r"(^|/)(raw|runs|archive|attempts)(/|$)|-evidence(/|$)")
_CONTROL_NAME = re.compile(r"(?i)(control|negative|mutation|mutant|counterproof|falsifier)")


def context_of(path: str) -> str:
    p = path.replace("\\", "/")
    if _EVIDENCE_SEG.search(p):
        return "evidence_copy"
    if _CONTROL_NAME.search(os.path.basename(p)):
        return "control"
    return "production"


def scan_text(text: str, path: str, blob: str | None = None) -> list[dict]:
    out = []
    ctx = context_of(path)
    errors: list = []
    found = []
    for name, ln, cl, first, plus, follow in lex_tokens(text, errors):
        r = classify_token(name, first, plus, follow)
        if r is not None:
            found.append((ln, cl, name.replace("\x00", "«").replace("\x01", "."), r))
    for ln, cl, kind in errors:
        found.append((ln, cl, "", (kind, "A", "error")))
    for ln, cl, token, (kind, layer, sev) in sorted(found, key=lambda x: (x[0], x[1])):
        f = {"path": path, "line": ln, "col": cl, "token": token, "kind": kind,
             "layer": layer, "severity": sev, "context": ctx}
        if blob:
            f["blob"] = blob
        out.append(f)
    return out


def iter_fs(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if d != ".git")
                for fn in sorted(files):
                    if fn.endswith(".lean"):
                        full = os.path.join(root, fn)
                        yield os.path.relpath(full, p), full
        elif p.endswith(".lean"):
            yield p, p


def git_lean_blobs(repo: str, rev: str):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    ls = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", rev],
                        check=True, capture_output=True, env=env).stdout
    entries = []
    for rec in ls.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, sha = meta.split()
        p = path.decode("utf-8", "surrogateescape")
        if typ == b"blob" and p.endswith(".lean"):
            entries.append((p, sha.decode()))
    if not entries:
        return
    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    try:
        for p, sha in entries:
            proc.stdin.write(sha.encode() + b"\n")
            proc.stdin.flush()
            header = proc.stdout.readline().split()
            size = int(header[2])
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
    ap.add_argument("--fail-on", default="production")
    args = ap.parse_args(argv)
    if not args.paths and not args.git:
        ap.print_usage(sys.stderr)
        return 2
    findings: list[dict] = []
    files = 0
    undecodable = []
    try:
        if args.git:
            for p, sha, data in git_lean_blobs(args.git, args.rev):
                files += 1
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    undecodable.append(p)
                    continue
                findings += scan_text(text, p, sha)
        for rel, full in iter_fs(args.paths):
            files += 1
            try:
                with open(full, encoding="utf-8") as fh:
                    text = fh.read()
            except UnicodeDecodeError:
                undecodable.append(rel)
                continue
            findings += scan_text(text, rel)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"layer_a_scan: error: {exc}", file=sys.stderr)
        return 2
    fail_ctx = None if args.fail_on == "all" else set(args.fail_on.split(","))
    failing = [f for f in findings if f["severity"] in ("violation", "error")
               and (fail_ctx is None or f["context"] in fail_ctx)]
    summary = {"files": files, "findings": len(findings),
               "violations": sum(f["severity"] == "violation" for f in findings),
               "errors": sum(f["severity"] == "error" for f in findings),
               "failing": len(failing), "undecodable": undecodable}
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "findings": findings}, fh, indent=1, ensure_ascii=False)
    for f in failing:
        print(f"{f['path']}:{f['line']}:{f['col']}: {f['layer']} {f['kind']} ({f['context']})")
    print(json.dumps(summary, ensure_ascii=False))
    # Undecodable files cannot be certified clean: fail closed.
    if undecodable:
        return 1
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
