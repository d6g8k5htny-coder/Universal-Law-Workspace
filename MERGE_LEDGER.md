# MERGE_LEDGER — every merge performed, with base, head, conflicts and effect

**Scientific effect of every row: NONE.** No merge below flipped a `lemma_closed`
flag, a prize disposition, a `LANDING_CLAIMS` or `PROOF_INDEX` entry, or a theorem
status. No proof was rewritten to fit a monorepo. No default branch was changed.

Merges are listed newest last. "Inside a package" means the merge stayed within one
repository and that repository's own CI was already about that change.

---

## 1. `main` — base into `claude/firewalls-fail-closed` (first base merge)

| | |
|---|---|
| repository | `main` |
| base merged in | `chatgpt/drive-github-hardening-20260919` @ `2f7a5a9f10c9…` |
| head before | `9e36788` |
| merge commit | `19f9b66` |
| kind | ordinary merge, inside a package |
| conflicts | **2, both in `claims/README.md`** |
| resolution | **Both sides kept.** The base had added a tenth firewall row (`FW-RUNG-OPEN-PREMISE`); the branch had rewritten the `FW-UNCONDITIONAL` row. Neither was discarded: the table carries both rows, and the prose counts were moved to the merged graph (26 claims, 10 firewalls). No winner was picked on any status word. |
| scientific effect | NONE |

## 2. `main` — base into `claude/firewalls-fail-closed` (refresh to current base)

| | |
|---|---|
| base merged in | `chatgpt/drive-github-hardening-20260919` @ `cd66a655d0a9…` |
| head before | `d4ab3618a075…` |
| merge commit | `1db16d1f59f4…` |
| kind | ordinary merge, inside a package |
| conflicts | none — the base delta touched `research/PINNED_SOURCES.md`, `tests/test_pinned_sources.py` and the SIDE24 custody tree, disjoint from this branch's three files |
| validated before push | full suite 3450 passed / 2 skipped; `claims_check` `problems=0`; `pinned_sources_check`, `consumers_check`, `verify_manifests`, `closure_pipeline check-plan` clean; 105 targeted tests |
| scientific effect | NONE |

## 3. `main` — base into `claude/interval-docs-errata`

| | |
|---|---|
| base merged in | `chatgpt/drive-github-hardening-20260919` @ `cd66a655d0a9…` |
| head before | `0b2e3be97a3b…` |
| merge commit | `a20e4cf255aa…` |
| kind | ordinary merge, inside a package |
| conflicts | none (same disjoint base delta) |
| validated before push | full suite 3420 passed / 2 skipped; 100 targeted tests; `pinned_sources_check`, `claims_check`, `verify_manifests` clean |
| scientific effect | NONE |

## 4. `query-` — PR #14 into PR #13's branch (**the Part A merge**)

| | |
|---|---|
| repository | `query-` |
| base | `chatgpt/src-migration-20260925` @ `f186847dbe32…` (PR #13) |
| head merged in | `copilot/fix-github-actions-job` @ `99372d3c9e7e…` (PR #14) |
| result | **fast-forward** to `99372d3c9e7e…` on the new branch `integration/public-src-20260926` |
| kind | fast-forward, inside a package |
| authorised because | PR #14 exists solely to clear the TIP_DRIFT failure on PR #13's CI, and PR #14's own CI run 36245871219 attempt 2 was already green on exactly that change |
| conflicts | none — a clean fast-forward, so PR #13's history is preserved unmodified and PR #14's commits keep their authorship |
| conflict NOT resolved by this merge | `query-` PR #12 refreshes the same gate stubs on a different base. **Not merged.** See `CONFLICT_LEDGER.md`. |
| scientific effect | NONE |

## 5. `query-` — the one commit added on top

| | |
|---|---|
| commit | `6c8389bf8566…` on `integration/public-src-20260926` |
| what | `portable/FEDERATION_IDENTITY_TRANSITION.json` and `tests/test_federation_identity.py`, plus a README section |
| why it is not a merge | it is new content, recorded here so the branch's provenance is complete: #13 + #14 + exactly one commit |
| scientific effect | NONE |

---

## Merges deliberately NOT performed

| proposed merge | why not |
|---|---|
| `query-` `integration/public-src-20260926` → `query-` **`main`** | This would change a **public default branch**. PR [#16](https://github.com/d6g8k5htny-coder/query-/pull/16) is green and one click away, but it is unreviewed, and the standing instruction is that default branches stay the public reviewed tips. Left to the owner. |
| `query-` PR #12 → anything | Overlaps PR #14's gate-stub refresh on a different base. Merging either one would pick a winner between two refresh routes. Recorded in `CONFLICT_LEDGER.md` instead. |
| anything → `Math-` **`main`** | No integration merge belongs on `Math-`'s default branch. None was performed, proposed or staged. |
| the 17 unlisted open `Math-` PRs, and `main` PRs #135/#136 | Not on the instructed include list. Recorded in `BRANCH_MAP.md` as decisions rather than swept in. |
| any merge mixing author-side AMEND math into an ACCEPTed landing path | **None was attempted.** No merge in this ledger crosses that boundary; had one been required, the instruction is to stop and record it, and that is what the row above for PR #12 does. |

## What this ledger does not establish

Every row is a git operation. A clean merge means git reconciled two trees without
textual conflict — it does not mean the result is mathematically sound, that any
bound holds, or that any review obligation is discharged. The CI evidence cited is
execution evidence: a green run is a run.
