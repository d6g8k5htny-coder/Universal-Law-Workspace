# BRANCH_MAP — every ref this workspace includes, and why
**Scientific effect: NONE.** Every row below is a git reference and a reason for including it. No row asserts that any theorem, lemma, prize or bound is accepted, and nothing here changes a claim status in any package.
Generated from [`WORKSPACE.json`](WORKSPACE.json) by `scripts/generate_ledgers.py`, as of 2026-09-26. Do not hand-edit the SHAs here; edit the manifest and regenerate.
## Excluded by instruction
- **`sandbox`** (private) — Private. Out of scope by instruction; never cloned, read, copied or referenced by content in this repository.

## Included refs

### `main` — q0 / SIDE24 research program: registers, claim graph, engine, drive source map, checkers
Submodule `repos/main` is pinned at the **default tip** `99f8c2b7db3c530bf554ff90fdef89cd57fc29d8` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `99f8c2b7db3c…` | Public reviewed tip. This is the submodule pin for repos/main. |
| `chatgpt/drive-github-hardening-20260919` | research-tree | — | `cd66a655d0a9…` | The active research tree. Included BY NAME and explicitly NOT presented as default main. It is not the reviewed tip and this repository does not treat it as one. |
| `chatgpt/sard-g-execution-repair-20260925` | open-pr | [#122](https://github.com/d6g8k5htny-coder/main/pull/122) | `a1fc9581291b…` | Listed. SARD-G repair: countable open charts and endpoint-support localization. |
| `claude/firewalls-fail-closed` | open-pr | [#134](https://github.com/d6g8k5htny-coder/main/pull/134) | `1db16d1f59f4…` | Listed. Claim-graph firewalls converted to fail closed; gating CI green. |
| `claude/github-chatgpt-xxw5kp` | open-pr | [#21](https://github.com/d6g8k5htny-coder/main/pull/21) | `67de1a2111da…` | Listed. Architectural admission attestations and salvaged H3 review artifacts. |
| `cursor/intermediate-scale-bridge-ab2f` | open-pr | [#128](https://github.com/d6g8k5htny-coder/main/pull/128) | `674f88cd60fd…` | Listed. D5 intermediate-scale envelope between fixed annulus and fixed remote. |

### `Math-` — mathematical frontiers, coefficients, downstream hard gate; 21 of the 22 public catalog artifacts live here
Submodule `repos/Math-` is pinned at the **default tip** `10e1f191c7d9f2755ca971ddbba87874d2475619` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `10e1f191c7d9…` | Public reviewed tip. The downstream gate stub pins in query- are refreshed against exactly this commit. |
| `chatgpt/lifetime-parent-congruence-erratum-20260926` | open-pr | [#64](https://github.com/d6g8k5htny-coder/Math-/pull/64) | `d573b99d8792…` | Listed. |
| `chatgpt/pin-micro-covariance-20260926` | open-pr | [#60](https://github.com/d6g8k5htny-coder/Math-/pull/60) | `ad27c6b88021…` | Listed. |
| `cursor/d5-pin-microdisk-c059` | open-pr | [#69](https://github.com/d6g8k5htny-coder/Math-/pull/69) | `ae45d35192c2…` | Listed. |
| `cursor/proof-custody-repair-8e33` | open-pr | [#70](https://github.com/d6g8k5htny-coder/Math-/pull/70) | `b39e9ff77646…` | Listed. |

### `query-` — read-only exact-source lookup CLI and portable stub verifier
Submodule `repos/query-` is pinned at the **default tip** `a61656fc7cbe704f5b874e1cae08637fb914227f` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `a61656fc7cbe…` | Public reviewed tip. NOTE: this tip has NO src/ tree; the src tree is the proposal below. |
| `chatgpt/src-migration-20260925` | open-pr | [#13](https://github.com/d6g8k5htny-coder/query-/pull/13) | `f186847dbe32…` | Listed. Publishes the canonical universal_law_query src package with compatibility wrappers. |
| `copilot/fix-github-actions-job` | open-pr | [#14](https://github.com/d6g8k5htny-coder/query-/pull/14) | `99372d3c9e7e…` | Listed. Refreshes the downstream gate stub identities that were failing CI as TIP_DRIFT. Based on PR 13's branch, not on main. |
| `integration/public-src-20260926` | open-pr | [#16](https://github.com/d6g8k5htny-coder/query-/pull/16) | `6c8389bf8566…` | PR 13 fast-forwarded onto PR 14 plus the federation identity control the pair was missing. This is the branch that actually satisfies Part A. CI success. |

### `trial` — cross-repository federation controls and bounded public replay
Submodule `repos/trial` is pinned at the **default tip** `ff373ea56dfdbe99d83701c20c5e083a984b9bb6` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `ff373ea56dfd…` | Public reviewed tip. |

### `governance-` — operator protocols and governance records
Submodule `repos/governance-` is pinned at the **default tip** `7476e29c65ce82d23e0b39e7f7d98741a875a8ff` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `7476e29c65ce…` | Public reviewed tip. |

### `meta-framework` — the curated public catalog (registry.json, 22 artifacts)
Submodule `repos/meta-framework` is pinned at the **default tip** `14f6836e7ccf6a463ef6da745602debfea4d15ee` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `14f6836e7ccf…` | Public reviewed tip. |

### `google-drive` — Drive-side public surface; source of 1 of the 22 catalog artifacts
Submodule `repos/google-drive` is pinned at the **default tip** `ea55c6e76edb31c48da5ce5aa0c3761d3ee49146` (`main`).

| ref | kind | PR | sha | why |
|---|---|---|---|---|
| `main` | default | — | `ea55c6e76edb…` | Public reviewed tip. |

## Open, and deliberately NOT imported
An omission recorded is a decision; an omission unrecorded is an oversight. These are decisions.

| repo | ref | PR | why not |
|---|---|---|---|
| `main` | `claude/interval-docs-errata` | #135 | Open, and green, but NOT on the instructed include list, and it touches documentation and interval controls rather than src or publication. Recorded here so the omission is a decision, not an oversight. |
| `main` | `claude/noncertifying-label-enforcement` | #136 | Open, but NOT on the instructed include list; it enforces a float-labelling rule rather than touching src or publication. Recorded as a decision. |
| `query-` | `cursor/peer-handoff-meta6-3c3cf11-2393` | #12 | Open, and it ALSO refreshes downstream gate stubs on base main -- overlapping work with PR 14. Not on the include list. Flagged in CONFLICT_LEDGER.md rather than imported, because importing both refresh routes would require picking a winner. |
| `Math-` | *(all others)* | — | Math- has 21 open PRs; only the four listed (60, 64, 69, 70) are imported. The remaining 17 are not stale-branch noise to be swept in, and the instruction is explicit that every stale remote-tracking branch stays out. |

## This repository's own refs (the host, not a mapped package)
`universal-law-workspace` is where this map lives. This repository is NOT one of the seven mapped packages. It is the host. Its own refs are recorded here so a second bootstrap lane is visible rather than discovered by collision.

Root commit `fcd1d01ed87b…`, created 2026-09-26; coordination issue [#1](https://github.com/d6g8k5htny-coder/universal-law-workspace/issues/1).

| ref | kind | sha | why |
|---|---|---|---|
| `main` | default | `fcd1d01ed87b…` | The repository-creation commit, made by the owner. Left exactly as it is: this proposal descends from it by an ordinary merge and does not replace it. |
| `chatgpt/federation-bootstrap-20260926` | other lane | `fcd1d01ed87b…` | The second bootstrap lane named in issue #1. At the time this manifest was written it holds no work beyond the root commit -- same sha as main. Not touched, not merged, not rebased. See CONFLICT_LEDGER.md C5. |
| `claude/public-workspace-proposal-20260926` | this proposal | *(HEAD)* | This branch. Its sha is not written here because a manifest cannot contain the hash of the commit that contains it; the verifier resolves HEAD instead and checks that HEAD descends from root_commit. |

## How the named branches are materialised
The submodule gitlink pins ONE commit per package — the public reviewed default tip. The other named refs are not squashed away and are not silently absent: each is recorded above with its exact SHA, and `scripts/fetch_named_branches.sh` fetches every one of them into the corresponding submodule as a real local ref, so they become branches you can check out and diff. Nothing is copied into this repository to achieve that.
