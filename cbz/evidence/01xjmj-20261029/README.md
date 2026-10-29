# CBZ-0 Phase 1 evidence — cross-repository Layer A scan and ref classes

Contributor: Anthropic Claude, Claude Code session `session_01XjmjBhHbkztFy4aSubbtiS`
(01XJMJ). Discovery and tooling only, under the owner's 29 October CBZ-0 directive
and main#684's B-003: the canonical STATUS/GOVERNANCE/DECISIONS/TOOLING files and
all ref cleanup belong to the single canonical integrator. Nothing here closes,
merges, deletes or rewrites anything.

Observed: 2026-10-29, about 17:05Z, from full (non-shallow) fetches.

## Files

| File | Contents |
|---|---|
| `layer_a_tip_scan.json` | Scanner summary per repository at its default tip |
| `layer_a_branch_scan.json` | Scanner summary for every remote branch of `main` (318) and `Math-` (149) |
| `branch_classes.json` | Every non-default remote branch of all nine repositories: tip SHA, last commit date, class |

Branch classes: `MERGED_NO_PR` (tip is an ancestor of the default branch, not an open-PR
head), `UNMERGED_NO_PR`, `OPEN_PR_HEAD`. The class is the observation only; it is
not a disposition.

## Default tips scanned

| Repository | Tip | `.lean` files | Violation tokens |
|---|---|---:|---:|
| main | `4ef1867175dbe1072a54a02e95f80c4e2c70a4ff` | 4 | 0 |
| Math- | `8151f592918a845bf19eb8eafaf8444540a32734` | 162 | 0 |
| Universal-Law-Workspace | `45a80ab01504936b46d035c2de1f92c73ed273de` | 0 | 0 |
| governance- | `e396002a` | 0 | 0 |
| query- | `fb4c457b` | 0 | 0 |
| meta-framework | `c70e1984` | 0 | 0 |
| d6g8k5htny-coder | `eb98251e` | 0 | 0 |
| research-hosted-qualification | `2ec8cc66` | 0 | 0 |
| openclaw-custodian-validation | `83e0ba03` | 0 | 0 |

Full SHAs are in the JSON files.

## Findings

1. **All 149 `Math-` remote branches have zero violation tokens**, including the open
   Math-#514 branch and every evidence copy under it.
2. **Three `main` branches carry violation tokens, all in session-recovery scratch**:
   - `claude/determined-bardeen-mrqy4y` (8 tokens, `recovery/session_015wNj8…/scratch/inv/*.lean`);
   - `claude/nice-maxwell-7i7ok0` (6, `recovery/session_017Mi3hx…/increment2/local_lean_evidence/math_formal_partial_gate/{sorry,native,custom_imported}.lean`, which are deliberate negative-control fixtures, plus `scratch/v15/Joint.lean`);
   - `claude/recovery-01cz-20261013` (63, mostly `Reject{Sorry,NativeDecide,CustomAxiom}.lean` negative-control fixtures).

   None of these is on a default branch. Any archive or quarantine of these refs should
   record that their Lean files are scratch or negative controls, never closed proofs.
3. Branch classes per repository (default branch excluded):

| Repository | MERGED_NO_PR | UNMERGED_NO_PR | OPEN_PR_HEAD |
|---|---:|---:|---:|
| Math- | 44 | 79 | 25 |
| governance- | 30 | 5 | 0 |
| meta-framework | 37 | 6 | 0 |
| query- | 6 | 15 | 0 |
| Universal-Law-Workspace | 2 | 3 | 0 |
| d6g8k5htny-coder | 2 | 0 | 1 |
| research-hosted-qualification | 0 | 1 | 1 |
| openclaw-custodian-validation | 0 | 0 | 1 |

`main`'s classes are in 014K's table at main#684/6503151021 (47 merged, 187 unmerged,
43 open-PR head or base).

## Tool: `tools/cbz/layer_a_scan.py`

Purpose: a lexical Layer A pre-check (gate G1 complement) that scans any directory or
any git tree (`--git REPO --rev REV`, read from object storage, no checkout), so one
session with access can cover every repository and every branch.

It certifies exactly this: no code token (outside comments, strings, char literals and
`«»` names) among `sorry`, `admit`, `sorryAx`, `admitGoal`, `mkSorry`, `axiom`,
`native_decide`, `ofReduceBool`, `ofReduceNat`, `trustCompiler`, `skipKernelTC`.
`Float`, `Float32`, `unsafe`, `implemented_by`, `extern` and line-initial `stop` are
reported for review. It does not certify compilation or the absence of placeholders
produced by metaprogramming without those tokens; kernel/axiom gates G2–G4 are
authoritative for that. Undecodable files fail closed.

Run:

```sh
python3 -I tools/cbz/layer_a_scan.py --git ../Math- --rev origin/main --json out.json
python3 -I tools/cbz/layer_a_scan.py path/to/dir --fail-on production
```

Self-verification (gate G0):

```sh
python3 -B -m unittest tests.test_cbz_layer_a_scan          # 23 behavioural tests
python3 -B -m unittest tests.test_cbz_layer_a_scan_mutants  # 26 mutants, all must be killed
```

Both were observed passing at this commit, in normal and `-O` mode, on CPython 3.13.16.
The workspace's `federation-contract` and `pins` workflows run the whole `tests/`
directory, so both suites also run in hosted CI.

Relation to other scanners: 014K's `main` `tools/cbz0/layer_a_scan.py` (main only; that
session has no Math-/Workspace access) and the CBZ-MATH-198 unit's supplemental scanner
cover overlapping ground. The canonical integrator decides which one `TOOLING.md`
admits. This one adds git-tree mode, interpolated and raw strings, char literals, `«»`
names, and a token-drop mutation harness. Its test cases may be folded into the
admitted scanner, and this tool deleted, if that is simpler.
