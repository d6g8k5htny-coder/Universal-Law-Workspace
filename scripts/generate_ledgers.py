#!/usr/bin/env python3
"""Generate BRANCH_MAP.md from WORKSPACE.json so no SHA is ever retyped.

Reads the manifest, writes the human-readable branch map. Records nothing about
mathematics: every row is a git ref and a reason. Scientific effect NONE.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
M = json.loads((ROOT / 'WORKSPACE.json').read_text(encoding='utf-8'))

KIND_ORDER = {'default': 0, 'research-tree': 1, 'open-pr': 2}


def main() -> int:
    out = []
    out.append('# BRANCH_MAP — every ref this workspace includes, and why\n')
    out.append('**Scientific effect: NONE.** Every row below is a git reference and a reason for '
               'including it. No row asserts that any theorem, lemma, prize or bound is accepted, '
               'and nothing here changes a claim status in any package.\n')
    out.append(f"Generated from [`WORKSPACE.json`](WORKSPACE.json) by "
               f"`scripts/generate_ledgers.py`, as of {M['as_of_utc']}. "
               f"Do not hand-edit the SHAs here; edit the manifest and regenerate.\n")
    out.append('## Excluded by instruction\n')
    for x in M['excluded_repositories']:
        out.append(f"- **`{x['name']}`** ({x['visibility']}) — {x['reason']}\n")
    out.append('\n## Included refs\n')
    by_repo: dict[str, list] = {}
    for row in M['named_branches']:
        by_repo.setdefault(row['repo'], []).append(row)
    for pkg in M['packages']:
        name = pkg['name']
        rows = sorted(by_repo.get(name, []), key=lambda r: (KIND_ORDER.get(r['kind'], 9), r['branch']))
        out.append(f"\n### `{name}` — {pkg['role']}\n")
        out.append(f"Submodule `repos/{name}` is pinned at the **default tip** "
                   f"`{pkg['default_tip']}` (`{pkg['default_branch']}`).\n\n")
        out.append('| ref | kind | PR | sha | why |\n|---|---|---|---|---|\n')
        for r in rows:
            pr = f"[#{r['pr']}](https://github.com/d6g8k5htny-coder/{name}/pull/{r['pr']})" if r['pr'] else '—'
            out.append(f"| `{r['branch']}` | {r['kind']} | {pr} | `{r['sha'][:12]}…` | {r['why']} |\n")
    out.append('\n## Open, and deliberately NOT imported\n')
    out.append('An omission recorded is a decision; an omission unrecorded is an oversight. '
               'These are decisions.\n\n')
    out.append('| repo | ref | PR | why not |\n|---|---|---|---|\n')
    for r in M['deliberately_not_imported']:
        ref = f"`{r['branch']}`" if r['branch'] else '*(all others)*'
        pr = f"#{r['pr']}" if r['pr'] else '—'
        out.append(f"| `{r['repo']}` | {ref} | {pr} | {r['why_not']} |\n")
    h = M.get('host_repository')
    if h:
        out.append('\n## This repository\'s own refs (the host, not a mapped package)\n')
        out.append(f"`{h['name']}` is where this map lives. {h['note']}\n\n")
        out.append(f"Root commit `{h['root_commit'][:12]}…`, created {h['created_utc']}; "
                   f"coordination issue "
                   f"[#{h['coordination_issue']}]({h['url']}/issues/{h['coordination_issue']}).\n\n")
        out.append('| ref | kind | PR | sha | why |\n|---|---|---|---|---|\n')
        for r in h['refs']:
            sha = f"`{r['sha'][:12]}…`" if r.get('sha') else f"*({r.get('resolves_to', 'unset')})*"
            pr = f"[#{r['pr']}]({h['url']}/pull/{r['pr']})" if r.get('pr') else '—'
            out.append(f"| `{r['branch']}` | {r['kind']} | {pr} | {sha} | {r['why']} |\n")

    out.append('\n## How the named branches are materialised\n')
    out.append('The submodule gitlink pins ONE commit per package — the public reviewed default '
               'tip. The other named refs are not squashed away and are not silently absent: each '
               'is recorded above with its exact SHA, and `scripts/fetch_named_branches.sh` fetches '
               'every one of them into the corresponding submodule as a real local ref, so they '
               'become branches you can check out and diff. Nothing is copied into this repository '
               'to achieve that.\n')
    (ROOT / 'BRANCH_MAP.md').write_text(''.join(out), encoding='utf-8')
    print('BRANCH_MAP.md written:',
          len(M['named_branches']), 'included refs,',
          len(M['deliberately_not_imported']), 'recorded omissions,',
          len((M.get('host_repository') or {}).get('refs', [])), 'host refs')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
