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
| `a3_float_census.json` | Layer A3 float-use census per repository at its default tip: class counts and the triage-first list |

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

## Layer A3 float-use census

Tool: `tools/cbz/a3_float_census.py` (standard library, AST-based, git-tree mode like the
Lean scanner). A3 forbids floating-point *certification* of bounds. Whether a float
certifies anything is a question about intent, so the tool is an inventory, not a
verdict: per Python file it records every point where floating point can enter
(float or complex literals, `float()`/`complex()`, `/` and `/=`, inexact `math`/`cmath`
functions, numpy/scipy/mpmath/decimal/cmath imports) and the exact or interval
machinery the file uses (fractions, sympy, python-flint, gmpy2, `mpmath.iv`,
`math.nextafter`/`math.ulp`, or an `ia` interval module). Classes: `NO_FLOAT_SIGNAL`,
`FLOAT_SIGNAL` (float signals and no exact or interval machinery), `MIXED`,
`UNPARSEABLE` (fails closed, exit 1).

| Repository | Tip | `.py` files | FLOAT_SIGNAL | MIXED | NO_FLOAT_SIGNAL | UNPARSEABLE |
|---|---|---:|---:|---:|---:|---:|
| main | `4ef18671` | 339 | 233 | 66 | 40 | 0 |
| Math- | `8151f592` | 668 | 249 | 395 | 24 | 0 |
| query- | `fb4c457b` | 28 | 24 | 0 | 4 | 0 |
| meta-framework | `c70e1984` | 17 | 14 | 0 | 3 | 0 |
| governance- | `e396002a` | 4 | 2 | 1 | 1 | 0 |
| Universal-Law-Workspace | `45a80ab0` | 8 | 6 | 0 | 2 | 0 |

The other three repositories have no Python files at their tips. Re-running the tool at
the recorded revisions reproduces every count above.

Triage-first rule (recorded in the JSON as `triage_first`): class `FLOAT_SIGNAL`, at least
one signal other than `/`, and a path matching
`(?i)(certif|enclos|bound|interval|verif|rigor|exact|proof|lemma|coefficient|constant)`.
Sorted by the number of non-division signals.

### Triage result

1. **Math-: no A3 candidate.** All 11 triage-first files are controls, diagnostics,
   tests or custody checks. None is a certificate:
   - `frontiers/third_order_coefficient_20261001/c2_check.py` is "Controls". Its NOTE's
     disposition is "FORMAL COEFFICIENT WITH NUMERICAL EVIDENCE" and its dependency
     paragraph says "No numerical input is consumed". The `c2` values are certified by
     the closed-form enclosures of merged Math-#223.
   - `frontiers/cusp_coefficient_certified_20261001/controls.py` and
     `frontiers/c2_exact_20261001/controls.py` are "Floating controls ... These are not
     part of the certificate".
   - `coefficients/d3_l4_anisotropic_20261005/source_crosscheck.py` is "diagnostic
     arithmetic, not interval evidence. The certificate's error bounds do not come from
     these comparisons".
   - `.../test_replay_metadata.py` and the four other `test_*` hits are unit tests with
     fixture floats.
   - `verify_packet.py` and `imports/upper2d_h5_ledgers_20260926/verify.py` are custody
     checks.

   The certificate engines are `MIXED`. For example,
   `frontiers/c8_elder_failure_coefficient_20261001/{certificate,boxes}.py` import a local
   `ia.py` whose operations are "widened outward by one ulp (math.nextafter), so each
   interval contains the exact real result". That is interval arithmetic, which A3
   permits. `MIXED` is still a census class and not a proof that every float in such a
   file is enclosed.
2. **main: two history files are A3 quarantine-label candidates.**
   - `history/carrier20_recovery_20260928/public_carriers/verify_wp_witness_v1.py`: 105
     non-division signals. It uses numpy, mpmath at floating precision and `float()`, and
     calls itself a certificate.
   - `.../verify_thm023_v1_1_v1.py`: 47 non-division signals.

   Neither is on a live verification path. The directory README already says these are
   "historical research sources, NOT newly accepted theorems", and the one code reference
   from live code (`experiments/h3_band_v2/h2/cov_exact.py`) is "consulted for
   cross-checking only". Older ledgers still cite the first file as a certificate:
   `KIMI-DER-025_wp_resolution.txt`, `CARRIER20_CUSTODY.json` and an incoming W3 bundle
   report.

   Proposed disposition for the canonical integrator: label both files "historical,
   float-based, not an A3-admissible certificate" where they are cited, and do not delete
   them (§9: no silent deletion).
3. **query-, meta-framework and the Workspace** have one triage-first hit each, and each is
   a test file (`tests/test_stub_verify_snapshot.py`,
   `catalog_tests/test_w8d_verify_refusal_control.py`,
   `tests/test_verify_pins_input_types.py`). None certifies a mathematical bound.
   **governance-** has none.

Self-verification (A8):

```sh
python3 -B -m unittest tests.test_cbz_a3_float_census   # 18 behavioural, harness control, 15 mutants
```

Every mutant (each signal, the exact-math list, interval-layer detection, the `MIXED`
class, the fail-closed exit and git mode) must be killed, or the suite fails. Both
mutation harnesses count a mutant as killed only if the suite loaded, ran and reported a
failing test; a suite that cannot import the tool is a survivor, not a kill. The census
harness also runs an unmutated copy through the same path and requires it to pass,
following Claude017's harness-control rule (main#684/6503454483). This census
does not replace review. A `FLOAT_SIGNAL` file is certification-relevant only if a
certificate depends on it.
