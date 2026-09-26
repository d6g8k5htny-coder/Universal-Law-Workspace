#!/usr/bin/env python3
"""Report whether each pinned default_tip is still its package's default tip.

Drift is a FACT TO REPORT, not an error: a pin is custody, and a package default
moving is the normal life of a repository. So this exits 0 whether or not it finds
drift, and exits nonzero only when it cannot do its job -- a malformed manifest, or
a package whose default branch it could not read at all. A reporter that failed the
build on drift would push whoever hit it toward deleting the pin rather than
recording the difference.

Needs network access to reach the public remotes. Without it, every row reads
UNREADABLE and the exit code says so, because "I could not look" must not print
the same as "nothing has changed".

Scientific effect: NONE. A commit identity is custody, not correctness.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def live_tip(owner: str, name: str, branch: str, timeout: int) -> str | None:
    url = f"https://github.com/{owner}/{name}.git"
    try:
        r = subprocess.run(["git", "ls-remote", url, f"refs/heads/{branch}"],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0 or not r.stdout.split():
        return None
    return r.stdout.split()[0]


def main(argv: list[str] | None = None) -> int:
    # argv is explicit so a caller -- a test, or another script -- is never at the
    # mercy of whatever sys.argv happens to hold. Reading sys.argv unconditionally
    # made the first controls for this file die in argparse on unittest's own flags.
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args(argv if argv is not None else sys.argv[1:])
    m = json.loads((ROOT / "WORKSPACE.json").read_text(encoding="utf-8"))
    owner = m["owner"]
    rows, drifted, unreadable = [], 0, 0
    for pkg in m["packages"]:
        pinned = pkg["default_tip"]
        got = live_tip(owner, pkg["name"], pkg["default_branch"], a.timeout)
        if got is None:
            state, unreadable = "UNREADABLE", unreadable + 1
        elif got == pinned:
            state = "current"
        else:
            state, drifted = "DRIFTED", drifted + 1
        rows.append((pkg["name"], pinned, got, state))

    width = max(len(r[0]) for r in rows)
    for name, pinned, got, state in rows:
        shown = (got or "-")[:12]
        print(f"{name:{width}}  pinned {pinned[:12]}  live {shown:12}  {state}")
    print(f"report_tip_drift: packages={len(rows)} current={len(rows) - drifted - unreadable} "
          f"drifted={drifted} unreadable={unreadable}")
    print("Drift is not an error. A pin is exactly those bytes; it never claimed to be the "
          "newest commit. This reports no mathematics and moves no status.")
    if unreadable:
        print(f"REFUSING: {unreadable} package default branch(es) could not be read, so this run "
              f"cannot distinguish 'unchanged' from 'not looked at'.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
