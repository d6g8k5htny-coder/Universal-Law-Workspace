# CONFLICT_LEDGER — where two trees disagree, both are kept

**No winner is picked in this file.** The standing instruction is that if two trees
disagree, both are kept and the disagreement is recorded. Every row below is a live
disagreement between public refs, left live on purpose.

**Scientific effect: NONE.** Recording a disagreement is not resolving it, and none of
these rows moves a theorem, lemma, prize or claim status.

---

## C1 — `query-`: two independent gate-stub refresh routes

| | |
|---|---|
| tree A | PR [#14](https://github.com/d6g8k5htny-coder/query-/pull/14) `copilot/fix-github-actions-job` @ `99372d3c9e7e…`, base = **PR #13's branch** |
| tree B | PR [#12](https://github.com/d6g8k5htny-coder/query-/pull/12) `cursor/peer-handoff-meta6-3c3cf11-2393`, base = **`main`** |
| both change | `portable/CANDIDATE_DOWNSTREAM_GATE_STUBS.json` — the same pinned identities |
| disagreement | different bases and different refresh generations. #12's body records a refresh to Math tip `703e947`; #14 refreshes to `10e1f191…`, which is the current default tip. |
| what was done | **#14 was merged (fast-forward) because it is the fix for #13's own failing CI. #12 was left untouched and unmerged.** Its branch, its PR and its history are intact. |
| what was NOT done | No attempt to reconcile the two, and no claim that either is correct. Merging both would require choosing which refresh generation is authoritative; that is the owner's call, not a merge. |
| how to see the disagreement | `git -C repos/query- diff origin/main origin/cursor/peer-handoff-meta6-3c3cf11-2393 -- portable/` against the same diff for `#14`'s branch |

## C2 — `query-`: `research_query.py` has two legitimate identities

| | |
|---|---|
| tree A | `main` @ `a61656fc7cbe…` — **5577 bytes**, sha256 `54105dcd723e71b1…`, the canonical implementation |
| tree B | `integration/public-src-20260926` @ `6c8389bf8566…` — **541 bytes**, sha256 `b49d32fed78ee78f…`, a compatibility wrapper |
| disagreement | the same path holds different bytes with different roles, and an external consumer pins the A identity |
| what was done | **Both identities recorded**, in `query-/portable/FEDERATION_IDENTITY_TRANSITION.json` and in this workspace's `IDENTITY_LEDGER.md`. The A identity was **not** overwritten in the record and the A pin in `trial/federation/replay.py` was **not** repointed. |
| why neither is "the winner" | A is what `trial/federation/replay.py` fetches at immutable commit `8e201316…` and will keep fetching. B is what a `main`-merged src tree would present. Both are true of their own ref. |

## C3 — `main`: `claims/README.md` firewall table, resolved by keeping both sides

| | |
|---|---|
| tree A | `chatgpt/drive-github-hardening-20260919` — added the `FW-RUNG-OPEN-PREMISE` row |
| tree B | `claude/firewalls-fail-closed` — rewrote the `FW-UNCONDITIONAL` row |
| disagreement | two textual conflicts in the same table during the base merge |
| what was done | **both rows kept** in merge `19f9b66`; the prose counts were then reconciled to the merged graph (26 claims, 10 firewalls). No status word was decided by the merge. |
| residue | none — this one is genuinely resolved, and is listed so the ledger is not read as covering only unresolved cases |

## C4 — `main`: default branch vs research tree

| | |
|---|---|
| tree A | `main` @ `99f8c2b7db3c…` — the public reviewed default |
| tree B | `chatgpt/drive-github-hardening-20260919` @ `cd66a655d0a9…` — the active research tree, where nearly all current work lands |
| disagreement | they are far apart, and the research tree is where the live checkers and registers are |
| what was done | **both are named in `BRANCH_MAP.md`**, the submodule pin is the *default* tip, and the research tree is labelled a research tree. This workspace does not present B as if it were the default. |
| explicitly not done | no merge of B into A, and no relabelling of either |

## C5 — this repository: two bootstrap lanes, both now real

| | |
|---|---|
| tree A | `chatgpt/federation-bootstrap-20260926` @ `d72ccbe3044b…`, PR [#2](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/pull/2) — federation contract (`workspace/repositories.json`), a fail-closed validator (`tools/check_workspace.py`), 8 contract tests, read-only CI, design and plan notes |
| tree B | `claude/public-workspace-proposal-20260926` @ this branch, PR [#3](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/pull/3) — repository map (`WORKSPACE.json`), validator (`scripts/verify_workspace.py`), seven submodule gitlinks, four ledgers, 26 negative controls, CI |
| disagreement | **real, and now byte-level.** [Issue #1](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/issues/1) assigns the map / validator / controls / CI slice to lane A; lane B had built a map and a validator before the issue existed. Colliding paths: `README.md`, `tests/`, and `.github/workflows/` (different filenames, so **both** workflows would run on a merged tree). Everything else is disjoint — A uses `workspace/` + `tools/`, B uses `WORKSPACE.json` + `scripts/`. |
| earlier state, corrected | a previous revision of this row said tree A held no work beyond the root commit. That was true when written and is **no longer true**: A advanced from `fcd1d01` to `d72ccbe3` while B was being prepared. The row is corrected rather than quietly restated, and `WORKSPACE.json` carries the current sha. |
| what was done | **Nothing of lane A's was overwritten, rebased or force-pushed.** B descends from `fcd1d01` by an ordinary merge, so A branches from an unchanged `main`. B's paths were posted on issue #1 and on PR #2, as that issue requests. B reviewed A on PR #2 and returned **AMEND** with one blocking fail-open and a verified patch, **without pushing to A's branch**. |
| what was NOT done | No merge either way. No merge of B into `main`. A's branch untouched. No claim that either map or either validator is the right one — and B did not resolve the duplication in its own favour by landing first. |
| the review's standing | **zero organizational independence credit.** B's review of A is a technical verdict from the author of a competing proposal in the same repository, for the same owner. The conflict of interest is declared in the review itself. Any gate requiring organizational independence remains **OPEN**, and no amount of cross-review between two agents changes that. |
| residue | **live.** Two repository maps and two validators may exist in one repository. Neither can promote anything — both fail closed and assert only documentation facts — but the redundancy is unresolved here on purpose. A single validator over lane A's contract layer and lane B's custody layer is the obvious reconciliation; choosing it is the owner's call, not a merge's. |

---

## What this ledger does not establish

A recorded disagreement is not a resolved one. Nothing here says which tree is
mathematically right, which refresh generation is authoritative, or which branch should
become a default. It says only that both exist, where to look, and that nothing was
silently discarded to make the map tidy.
