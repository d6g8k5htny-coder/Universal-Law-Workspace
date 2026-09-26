# CONFLICT_LEDGER — where two trees disagree, both are kept

**No winner is picked in this file.** The standing instruction is that if two trees
disagree, both are kept and the disagreement is recorded.

Rows were all live when first written. Two have since been **resolved by the owner**, and
they are marked RESOLVED in place rather than deleted: a ledger that quietly drops a row
once it stops being convenient is worth less than no ledger. Each says what resolved it
and on what evidence, and the evidence was re-verified here rather than read off a
closing note. The header of this file previously asserted that every row was live; that
became false within the hour, and this paragraph is the correction.

**Scientific effect: NONE.** Recording a disagreement is not resolving it, and none of
these rows moves a theorem, lemma, prize or claim status.

---

## C1 — `query-`: two independent gate-stub refresh routes — **RESOLVED**

| | |
|---|---|
| tree A | PR [#14](https://github.com/d6g8k5htny-coder/query-/pull/14) `copilot/fix-github-actions-job`, base = **PR #13's branch** |
| tree B | PR [#12](https://github.com/d6g8k5htny-coder/query-/pull/12) `cursor/peer-handoff-meta6-3c3cf11-2393`, base = **`main`** |
| both changed | `portable/CANDIDATE_DOWNSTREAM_GATE_STUBS.json` — the same pinned identities, at different refresh generations (#12's body records Math tip `703e947`; #14 refreshes to `10e1f191…`, the current default tip) |
| how it resolved | the **owner** merged **#13** at `2026-09-26T15:08:30Z` and **#14** at `15:08:50Z`, and closed **#12** unmerged at `15:24:41Z`. `query-` `main`'s tip commit is the #14 merge. So the refresh generation that landed is the one pinned to the current `Math-` default tip. |
| what this map did | nothing. It recorded both routes and merged neither. The choice was made by the owner on the default branch, which is where it belonged. |
| residue | none on the refresh question. #12's branch, PR and history remain intact and unmerged, and its route is still readable there. |

## C2 — `query-`: `research_query.py` had two legitimate identities — **RESOLVED**

| | |
|---|---|
| tree A | `main` @ `a61656fc7cbe…` — **5577 bytes**, sha256 `54105dcd723e71b1…`, the canonical implementation |
| tree B | `integration/public-src-20260926` @ `6c8389bf8566…` — **541 bytes**, sha256 `b49d32fed78ee78f…`, a compatibility wrapper |
| the disagreement | the same path held different bytes with different roles, and an external consumer pins the A identity |
| how it resolved | the #13 merge put the **wrapper** on `main`. Recomputed here from the current default tip `76e1ca09a483…` rather than assumed: `research_query.py` is **541 bytes**, sha256 `b49d32fed78ee78f688fee8e224629000964bf2b285d59e669a4dfbe9f131bfe`, blob `0a89183d0499…` — byte-identical to tree B. There is now one identity on the default branch, not two. |
| the superseded identity is not lost | `a61656fc7cbe…:research_query.py` still resolves to **5577 bytes**, sha256 `54105dcd723e…`, checked. `trial/federation/replay.py` pins the superseded bytes at the **immutable commit** `8e201316…`, so it was never at risk and must still not be repointed. |
| what remains open, and is NOT a conflict | no file on `main` records the *transition* — the superseded identity, and the four downstream consumers with why each is unaffected. `portable/FEDERATION_IDENTITY_TRANSITION.json` and `tests/test_federation_identity.py` exist only at `6c8389bf8566…`, on the branch of the closed PR #16, and are recoverable from it. The live cross-repository interface *is* controlled on `main`, by `tests/test_wrapper_parity.py::test_wrapper_reexports_legacy_api`, which asserts exactly the names `trial` imports — verified by reading that file at the default tip. So this is a provenance gap, not an unguarded interface, and the owner's judgement that it can be extracted if a consumer needs it is consistent with what the bytes show. |

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
| tree A | `main` @ `70664bd66f77…` — the public reviewed default (it was `99f8c2b7db3c…` when this row was written; the default moved within the hour, which is the point `tip_freshness` in `WORKSPACE.json` now makes explicitly) |
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

A recorded disagreement is not a resolved one, and a row marked RESOLVED above says only
that the owner chose on the default branch and that the choice was verified from the bytes
— not that either tree was mathematically right. Nothing here says which tree is
mathematically right, which refresh generation is authoritative, or which branch should
become a default. It says only that both exist, where to look, and that nothing was
silently discarded to make the map tidy.
