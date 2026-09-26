#!/usr/bin/env python3
"""Verify this workspace describes itself truthfully. Refuses on any mismatch.

Checks, in order:
  1. every package in WORKSPACE.json has a submodule gitlink, and the gitlink SHA
     equals the recorded default tip -- the pin and the document cannot disagree;
  2. .gitmodules names exactly the recorded packages, with public https URLs;
  3. no in-scope package is missing and no extra submodule has appeared;
  4. no tracked file carries a credential, a private relay address, or a mention of the
     excluded private package outside the files allowed to declare the exclusion;
  5. every named branch row carries a 40-hex sha and a non-empty reason;
  6. BRANCH_MAP.md is not stale: every recorded sha AND every recorded branch name
     appears in it (a sha-only check is satisfied by a sibling row when two refs share
     a sha, and the ref itself can then vanish from the map unnoticed);
  7. every host-repository ref carries a 40-hex sha (or resolves to HEAD) and a reason,
     and appears in BRANCH_MAP.md;
  8. HEAD descends from the host repository's recorded root commit -- a branch that
     replaced the owner's history instead of building on it fails here;
  9. a vacuity floor per category -- an empty package list, ref list, omission list, host
     ref list or file scan is a failure for that category, not a pass, because one total
     can be propped up by growth in an unrelated category.

A pass is a documentation-consistency fact. It verifies no mathematics, accepts no
theorem and moves no status. Scientific effect: NONE.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HEX40 = re.compile(r'^[0-9a-f]{40}$')

# Assembled at runtime on purpose. A scanner that spells out the strings it forbids
# trips its own rule -- the first version of this file did exactly that, and the rule was
# right to flag it. Keeping the literals out keeps the rule honest about every file,
# including this one.
_RELAY_HOST = 'private' + 'relay.' + 'appleid' + '.com'
_RELAY_HOST_ALT = 'users.' + 'noreply.' + 'github' + '.com'


def main() -> int:
    m = json.loads((ROOT / 'WORKSPACE.json').read_text(encoding='utf-8'))
    problems: list[str] = []
    compared = 0

    gitlinks: dict[str, str] = {}
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-s', 'repos/'],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        mode, sha, _stage_path = line.split(' ', 2)
        _stage, path = _stage_path.split('\t', 1)
        if mode != '160000':
            problems.append(f'{path}: mode {mode}, expected 160000 (a submodule gitlink). '
                            f'A non-gitlink here means bytes were vendored without an '
                            f'IDENTITY_LEDGER row.')
        gitlinks[path.removeprefix('repos/')] = sha

    declared = {p['name']: p['default_tip'] for p in m['packages']}
    for name, tip in sorted(declared.items()):
        compared += 1
        got = gitlinks.get(name)
        if got is None:
            problems.append(f'{name}: declared in WORKSPACE.json and has no submodule gitlink')
        elif got != tip:
            problems.append(f'{name}: gitlink {got[:12]} != recorded default tip {tip[:12]}; '
                            f'the pin and the document disagree')
    for name in sorted(set(gitlinks) - set(declared)):
        problems.append(f'{name}: submodule present and not declared in WORKSPACE.json')

    gm = (ROOT / '.gitmodules').read_text(encoding='utf-8')
    for name in declared:
        compared += 1
        want = f'https://github.com/d6g8k5htny-coder/{name}.git'
        if want not in gm:
            problems.append(f'{name}: .gitmodules does not carry the public URL {want}; '
                            f'a stranger could not clone it')
    if 'file://' in gm or gm.count('url = /') or '\turl = ..' in gm:
        problems.append('.gitmodules carries a local or relative URL; a stranger cannot clone that')

    excluded = {x['name'] for x in m['excluded_repositories']}
    if 'sandbox' not in excluded:
        problems.append('sandbox is not recorded as an excluded repository')
    # Scan what is PUBLISHED, i.e. what git tracks -- not whatever happens to be on disk.
    # An untracked scratch file is not published and is not this checker's business; a
    # tracked one is. This also matters in the other direction: Python folds string
    # concatenation at compile time, so a __pycache__ entry contains the very literals its
    # source assembles at runtime to avoid carrying. Scanning raw disk therefore flagged
    # compiled bytecode that no clone of this repository will ever contain. The controls in
    # tests/ caught that.
    ls = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'],
                        capture_output=True, text=True)
    if ls.returncode != 0:
        problems.append(f'could not list tracked files (git exited {ls.returncode}: '
                        f'{ls.stderr.strip() or "no message"}). The secret scan cannot run, '
                        f'and a scan that cannot run is not a scan that passed.')
    tracked = [r for r in ls.stdout.split('\0') if r and not r.startswith('repos/')]
    for rel in sorted(tracked):
        path = ROOT / rel
        if not path.is_file():
            continue
        compared += 1
        text = path.read_text(encoding='utf-8', errors='replace')
        for bad in (_RELAY_HOST, _RELAY_HOST_ALT):
            if bad in text:
                problems.append(f'{rel}: contains a private relay address ({bad})')
        if re.search(r'gh[pousr]_[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY', text):
            problems.append(f'{rel}: looks like it contains a credential')
        if 'sandbox' in text and rel not in {
                'BRANCH_MAP.md', 'WORKSPACE.json', 'README.md', 'CONFLICT_LEDGER.md',
                'scripts/verify_workspace.py', 'IDENTITY_LEDGER.md'}:
            problems.append(f'{rel}: mentions sandbox outside the files allowed to declare '
                            f'the exclusion')

    branch_map = (ROOT / 'BRANCH_MAP.md').read_text(encoding='utf-8')
    for row in m['named_branches']:
        compared += 1
        if not HEX40.match(row['sha']):
            problems.append(f"{row['repo']}/{row['branch']}: sha is not 40 hex")
        if not row.get('why'):
            problems.append(f"{row['repo']}/{row['branch']}: included with no stated reason")
        if row['sha'][:12] not in branch_map:
            problems.append(f"{row['repo']}/{row['branch']}: sha {row['sha'][:12]} absent from "
                            f"BRANCH_MAP.md -- regenerate it from the manifest")
        # The name as well as the sha. Two refs can share a sha -- a branch cut from another
        # branch and not yet advanced -- and then a sha-only check is satisfied by the OTHER
        # row while this ref has silently vanished from the map. tests/ caught exactly that.
        if f"`{row['branch']}`" not in branch_map:
            problems.append(f"{row['repo']}/{row['branch']}: branch name absent from "
                            f"BRANCH_MAP.md -- regenerate it from the manifest")
    for row in m['deliberately_not_imported']:
        compared += 1
        if not row.get('why_not'):
            problems.append(f"{row['repo']}: omission recorded with no reason")

    host = m.get('host_repository')
    if not host:
        problems.append('WORKSPACE.json: no host_repository block -- the repository this map '
                        'lives in must be recorded, including any second bootstrap lane')
    else:
        root = host.get('root_commit', '')
        if not HEX40.match(root):
            problems.append('host_repository.root_commit is not 40 hex')
        for r in host.get('refs', []):
            compared += 1
            sha = r.get('sha')
            if sha is None:
                if r.get('resolves_to') != 'HEAD':
                    problems.append(f"host ref {r.get('branch')}: no sha and no resolves_to=HEAD")
                if f"`{r.get('branch')}`" not in branch_map:
                    problems.append(f"host ref {r.get('branch')}: absent from BRANCH_MAP.md")
            elif not HEX40.match(sha):
                problems.append(f"host ref {r.get('branch')}: sha is not 40 hex")
            elif sha[:12] not in branch_map:
                problems.append(f"host ref {r.get('branch')}: sha {sha[:12]} absent from "
                                f"BRANCH_MAP.md -- regenerate it from the manifest")
            if f"`{r.get('branch')}`" not in branch_map:
                problems.append(f"host ref {r.get('branch')}: branch name absent from "
                                f"BRANCH_MAP.md. This repository's refs include a second "
                                f"bootstrap lane; a lane that vanishes from the map is the "
                                f"failure this check exists for.")
            if not r.get('why'):
                problems.append(f"host ref {r.get('branch')}: recorded with no stated reason")
        if HEX40.match(root):
            compared += 1
            anc = subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor',
                                  root, 'HEAD'], capture_output=True, text=True)
            if anc.returncode == 1:
                problems.append(f"HEAD does not descend from the recorded root commit "
                                f"{root[:12]} -- this branch replaced the owner's history "
                                f"instead of building on it")
            elif anc.returncode != 0:
                problems.append(f"could not check ancestry of {root[:12]} "
                                f"(git exited {anc.returncode}: "
                                f"{anc.stderr.strip() or 'no message'}). A check that cannot run "
                                f"is not a check that passed.")

    # A vacuity floor PER CATEGORY, not one total. A single total is defeated by growth
    # somewhere unrelated: this file's floor was a flat `compared < 30`, and when two files
    # were added to the tree the tracked-file scan alone lifted the total back over it, so
    # the control that empties the whole manifest stopped failing and nothing said so. A
    # category cannot cover for another category.
    for empty, what in ((not declared, 'no packages declared'),
                        (not m['named_branches'], 'no named refs recorded'),
                        (not m['deliberately_not_imported'], 'no omissions recorded'),
                        (host is not None and not host.get('refs'),
                         'the host repository has no recorded refs'),
                        (not tracked, 'no tracked files scanned')):
        if empty:
            problems.append(f'VACUOUS RUN: {what}. A run that checked nothing in a category '
                            f'is not a pass for that category; the exit code would look the '
                            f'same if that part of the manifest had been deleted.')
    if compared < 30:
        problems.append(f'VACUOUS RUN: only {compared} comparisons in total. This is a coarse '
                        f'backstop behind the per-category floors above, not the main guard.')

    for p in problems:
        print(p)
    print(f'verify_workspace: packages={len(declared)} gitlinks={len(gitlinks)} '
          f'named_refs={len(m["named_branches"])} omissions={len(m["deliberately_not_imported"])} '
          f'host_refs={len((m.get("host_repository") or {}).get("refs", []))} '
          f'comparisons={compared} problems={len(problems)}')
    print('A pass is a documentation-consistency fact. It verifies no mathematics, accepts no '
          'theorem and moves no status.')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
