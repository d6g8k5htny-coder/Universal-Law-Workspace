#!/usr/bin/env python3
"""Compute IDENTITY_LEDGER.md from real bytes. Nothing here is typed by hand.

`--workspace DIR` must contain sibling public checkouts (query-, Math-, ...). Every
row is (repository, path, bytes, sha256, git blob) read off disk and out of git, so a
wrong number is a failed run rather than a wrong document.

Scientific effect NONE: a byte identity is custody, not correctness or acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]

# (repository, ref, path, role)
SUBJECTS = [
    ("query-", "integration/public-src-20260926", "portable/FEDERATION_IDENTITY_TRANSITION.json",
     "identity transition record authored for PR #16"),
    ("query-", "integration/public-src-20260926", "tests/test_federation_identity.py",
     "replacement control for the deleted pinned_federation_match step"),
    ("query-", "integration/public-src-20260926", "research_query.py",
     "compatibility wrapper (CURRENT identity)"),
    ("query-", "main", "research_query.py",
     "canonical implementation (SUPERSEDED identity)"),
    ("query-", "integration/public-src-20260926", "portable/CANDIDATE_DOWNSTREAM_GATE_STUBS.json",
     "downstream gate stub bundle, refreshed to the Math- default tip"),
]
# (ref, path, role) read out of THIS repository's own history, not a sibling checkout.
# The workspace was created with a GitHub auto-init README stub; this branch replaces it.
# The stub is recorded rather than silently dropped, and stays reachable at its commit.
SELF_SUBJECTS = [
    ("fcd1d01ed87b2d9c3bda7a9d13e64bb65ff4b0b1", "README.md",
     "auto-init stub present when the repository was created (SUPERSEDED by this branch, "
     "still reachable at that commit)"),
]

# Math- gate artifacts, at the default tip the stubs pin
GATE = "frontiers/downstream_gate_20260925"
GATE_FILES = ["README.md", "SCOPE.md", "hard_gate.py", "test_hard_gate.py",
              "RESULTS.json", "run_validation.py", "GRAPH.json"]


def ident(repo_dir: pathlib.Path, ref: str, path: str) -> dict | None:
    raw = subprocess.run(["git", "-C", str(repo_dir), "show", f"{ref}:{path}"],
                         capture_output=True)
    if raw.returncode != 0:
        return None
    blob = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", f"{ref}:{path}"],
                          capture_output=True, text=True).stdout.strip()
    return {"bytes": len(raw.stdout), "sha256": hashlib.sha256(raw.stdout).hexdigest(),
            "git_blob": blob}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--out", default=str(ROOT / "IDENTITY_LEDGER.md"))
    a = ap.parse_args()
    ws = pathlib.Path(a.workspace).resolve()
    m = json.loads((ROOT / "WORKSPACE.json").read_text(encoding="utf-8"))
    tips = {p["name"]: p["default_tip"] for p in m["packages"]}

    rows, missing = [], []
    for repo, ref, path, role in SUBJECTS:
        d = ws / repo
        got = ident(d, ref, path) if d.is_dir() else None
        (rows if got else missing).append((repo, ref, path, role, got))
    for ref, path, role in SELF_SUBJECTS:
        got = ident(ROOT, ref, path)
        (rows if got else missing).append(("universal-law-workspace", ref, path, role, got))
    mathdir = ws / "Math-"
    for f in GATE_FILES:
        p = f"{GATE}/{f}"
        got = ident(mathdir, tips["Math-"], p) if mathdir.is_dir() else None
        (rows if got else missing).append(
            ("Math-", tips["Math-"], p, "downstream hard-gate artifact pinned by query-'s stub bundle", got))

    out = ["# IDENTITY_LEDGER — exact bytes for everything this proposal touches\n",
           "**Scientific effect: NONE.** A matching byte identity is *custody*: evidence that a "
           "file is the file it claims to be. It is not correctness, not currentness, and not "
           "acceptance of any theorem, lemma, prize or bound.\n",
           "\n## Nothing is copied into this repository\n",
           "Every package is a **submodule gitlink** (`mode 160000`) pinned at an exact commit. No "
           "proof body, stub, register or checker is duplicated here, so there is no second copy "
           "that can silently drift from its source. The rows below therefore record identities "
           "*in their home repositories* — what this proposal points at, and what it changed in "
           "`query-` — rather than a manifest of vendored files.\n",
           "\nIf a future revision does vendor bytes, every copied file must gain a row here with "
           "its origin repository, origin path, git blob and SHA-256 before the copy lands.\n",
           "\n## Rows\n",
           "| repository | ref | path | bytes | sha256 | git blob | role |\n",
           "|---|---|---|---|---|---|---|\n"]
    for repo, ref, path, role, d in rows:
        r = ref if len(ref) != 40 else ref[:12] + "…"
        out.append(f"| `{repo}` | `{r}` | `{path}` | {d['bytes']} | `{d['sha256'][:24]}…` | "
                   f"`{d['git_blob'][:12]}…` | {role} |\n")
    if missing:
        out.append("\n## Rows that could NOT be computed in this run\n")
        out.append("A row here means the checkout was absent, not that the identity is unknown to "
                   "the project. It is listed so the ledger is never silently short.\n\n")
        out.append("| repository | ref | path | role |\n|---|---|---|---|\n")
        for repo, ref, path, role, _ in missing:
            out.append(f"| `{repo}` | `{ref}` | `{path}` | {role} |\n")
    out.append("\n## The two identities that changed, and why they are recorded rather than restored\n")
    out.append("`query-/research_query.py` appears twice above. On `main` it is the canonical "
               "implementation; on the src-migration line it is a compatibility wrapper, so its "
               "bytes differ. The pre-migration workflow asserted the old byte count inline and "
               "that assertion was deleted in the same change that invalidated it. Re-asserting "
               "the old count would be false, so both identities are on record and the current one "
               "is pinned by a test. `trial/federation/replay.py` pins the superseded bytes at an "
               "immutable commit and is unaffected.\n")
    out.append("\n`universal-law-workspace/README.md` is the second. The repository was created "
               "with a 25-byte GitHub auto-init stub and this branch replaces it with the map. The "
               "stub is not deleted: `fcd1d01ed87b…` is a parent of this branch, so "
               "`git show fcd1d01:README.md` returns those bytes verbatim. `CONFLICT_LEDGER.md` C5 "
               "records why it was replaced rather than kept at a second path.\n")
    pathlib.Path(a.out).write_text("".join(out), encoding="utf-8")
    print(f"IDENTITY_LEDGER.md written: {len(rows)} computed rows, {len(missing)} uncomputed")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
