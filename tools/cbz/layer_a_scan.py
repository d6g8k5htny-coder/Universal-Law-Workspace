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
                      ``+native`` / ``native := <anything but false>``
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
file cannot be lexed reliably. A scan root that does not exist, a directory
that cannot be traversed, and an unknown ``--fail-on`` context are usage/IO
errors (exit 2), never an empty clean scan.

Context (production / evidence_copy / control) is decided from a
repository-relative path, so it does not depend on how a path is spelled:
for a filesystem input, the path relative to the enclosing git work tree,
else relative to the scan argument (a directory, or a file's parent); an
explicit ``--context-root DIR`` overrides both. Git-tree mode uses the
tree path.

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
                  (default: production); each must be one of production,
                  evidence_copy, control, or the single word "all".
  --context-root DIR  classify filesystem paths relative to DIR
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
# ofReduceBool. Both are recognised on code tokens, so comments and line
# breaks in between do not matter. ``native`` after a ``+`` is flagged even
# with a space between, and ``native :=`` with any value but the literal
# ``false`` is flagged (safe direction: ``x + native`` or ``native := flag``
# may be false positives, never misses).
CONTEXTS = ("production", "evidence_copy", "control")
# ``def native := ...`` names a declaration; it is not an option assignment.
_DECL_KEYWORDS = {"def", "abbrev", "theorem", "lemma", "opaque", "instance", "axiom"}
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


def _skip_trivia(text: str, j: int) -> int:
    """Index of the next code character at or after j (skips whitespace and comments)."""
    n = len(text)
    while j < n:
        if text[j].isspace():
            j += 1
        elif text.startswith("--", j):
            k = text.find("\n", j)
            j = n if k < 0 else k
        elif text.startswith("/-", j):
            depth = 0
            while j < n:
                if text.startswith("/-", j):
                    depth += 1
                    j += 2
                elif text.startswith("-/", j):
                    depth -= 1
                    j += 2
                    if depth == 0:
                        break
                else:
                    j += 1
        else:
            break
    return j


def _native_assignment(text: str, j: int):
    """After an identifier ``native`` ending at j: None if no ``:=`` follows,
    "false" if the assigned value is the literal ``false``, else "other"."""
    j = _skip_trivia(text, j)
    if not text.startswith(":=", j):
        return None
    j = _skip_trivia(text, j + 2)
    if text.startswith("false", j) and not (j + 5 < len(text) and _id_rest(text[j + 5])):
        return "false"
    return "other"


def lex_tokens(text: str, errors: list | None = None):
    """Yield (name, line, col, line_start, plus_before, native_assign) per code identifier.

    ``name`` is the full dotted identifier text; an escaped ``«...»``
    component becomes ``\x00`` plus its text (inner dots as ``\x01``), so it
    matches constant names but never a keyword. ``plus_before`` says the
    previous code token (comments and whitespace skipped) is ``+``;
    ``native_assign`` is _native_assignment() for an identifier ``native``.
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
    last_code = ""          # last code character outside comments and literals
    last_word = ""          # text of the last identifier token
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
            last_code = '"'
            continue
        if c == "'":
            m = _CHAR_LIT.match(text, i)
            advance(m.end() - i if m else 1)
            line_has_token = True
            last_code = "'"
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
            last_code = "a"
            last_word = ""
            yield ".".join(parts), start_line, start_col, start_first, False, None
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
            plus_before = last_code == "+"
            declared = last_code == "a" and last_word in _DECL_KEYWORDS
            last_code = "a"
            name = ".".join(parts)
            last_word = name
            yield (name, start_line, start_col, start_first, plus_before,
                   _native_assignment(text, i) if name == "native" and not declared else None)
            continue
        if c.isdigit():
            while i < n and (text[i].isalnum() or text[i] in "._"):
                advance(1)
            line_has_token = True
            last_code = "0"
            continue
        if not c.isspace():
            line_has_token = True
            last_code = c
        advance(1)
    for frame in stack:
        if frame[0] == "istr":
            errors.append((frame[1], frame[2], "unterminated_interpolated_string"))
            break


def classify_token(name: str, line_start: bool, plus_before: bool = False, native_assign=None):
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
    if name == "native" and (plus_before or native_assign == "other"):
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


def scan_text(text: str, path: str, blob: str | None = None, context_path: str | None = None) -> list[dict]:
    out = []
    cpath = context_path if context_path is not None else path
    ctx = context_of(cpath)
    errors: list = []
    found = []
    for name, ln, cl, first, plus, native_assign in lex_tokens(text, errors):
        r = classify_token(name, first, plus, native_assign)
        if r is not None:
            found.append((ln, cl, name.replace("\x00", "«").replace("\x01", "."), r))
    for ln, cl, kind in errors:
        found.append((ln, cl, "", (kind, "A", "error")))
    for ln, cl, token, (kind, layer, sev) in sorted(found, key=lambda x: (x[0], x[1])):
        f = {"path": path, "line": ln, "col": cl, "token": token, "kind": kind,
             "layer": layer, "severity": sev, "context": ctx, "context_path": cpath}
        if blob:
            f["blob"] = blob
        out.append(f)
    return out


def _raise(exc):
    raise exc


def _git_top(directory: str):
    """The enclosing git work tree of an absolute directory, or None."""
    d = directory
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _context_path(full: str, scan_base: str, context_root: str | None) -> str:
    full = os.path.abspath(full)
    if context_root is not None:
        rel = os.path.relpath(full, os.path.abspath(context_root))
        if rel == ".." or rel.startswith(".." + os.sep):
            raise ValueError(f"{full} is outside --context-root {context_root}")
        return rel.replace(os.sep, "/")
    base = _git_top(os.path.dirname(full)) or os.path.abspath(scan_base)
    return os.path.relpath(full, base).replace(os.sep, "/")


def iter_fs(paths, context_root: str | None = None):
    """Yield (display_path, full_path, context_path) for every .lean input file.

    A missing path or an untraversable directory raises OSError (fail closed)."""
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p, onerror=_raise):
                dirs[:] = sorted(d for d in dirs if d != ".git")
                for fn in sorted(files):
                    if fn.endswith(".lean"):
                        full = os.path.join(root, fn)
                        yield os.path.relpath(full, p), full, _context_path(full, p, context_root)
        elif not os.path.exists(p):
            raise FileNotFoundError(2, "scan root does not exist", p)
        elif p.endswith(".lean"):
            yield p, p, _context_path(p, os.path.dirname(os.path.abspath(p)), context_root)


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
    ap.add_argument("--context-root", metavar="DIR")
    args = ap.parse_args(argv)
    if not args.paths and not args.git:
        ap.print_usage(sys.stderr)
        return 2
    if args.fail_on == "all":
        fail_ctx = None
    else:
        fail_ctx = set(args.fail_on.split(","))
        if not fail_ctx <= set(CONTEXTS):
            print(f"layer_a_scan: error: --fail-on must name contexts from {', '.join(CONTEXTS)} "
                  f"or be 'all', got {args.fail_on!r}", file=sys.stderr)
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
        for rel, full, cpath in iter_fs(args.paths, args.context_root):
            files += 1
            try:
                with open(full, encoding="utf-8") as fh:
                    text = fh.read()
            except UnicodeDecodeError:
                undecodable.append(rel)
                continue
            findings += scan_text(text, rel, context_path=cpath)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"layer_a_scan: error: {exc}", file=sys.stderr)
        return 2
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
