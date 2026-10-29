# CBZ decision ledger

This file records the initial, bounded CBZ implementation decisions. The
workspace is being assessed; it is not yet CBZ-0.

- 2026-10-29 UTC · Phase 1 · C · Reconstructed an isolated local mirror of
  Universal-Law-Workspace commit `45a80ab01504936b46d035c2de1f92c73ed273de`.
  Its 19 tracked file blobs and eight gitlinks match that commit; the local
  commit is synthetic and is not the upstream commit. The submodules are not
  initialized. The existing structural check and offline pin check pass;
  66 local tests pass. Reason: establish a measurable baseline without relying
  on inaccessible direct GitHub network access. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · All eight existing submodule pins differ from
  the observed default tips. The existing `--network` mode treats drift and
  unavailable tip information as informational; it does not prove CBZ gate
  G7. Three canonical-input blobs match old pinned commits but differ at the
  observed current commits; the historical authority map is on a named
  non-default branch and is absent from the current main tree. Decision:
  build a strict current-tip mode with targeted negative controls; treat
  canonical-input reconciliation as separate work. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · B · Proposed strict pin verification must refuse
  skipped non-public entries, failed lookups, missing or inconsistent remote
  HEAD, missing configured branches, duplicate or conflicting advertised refs,
  and differing pinned/default tips. It must leave the existing non-strict
  mode and all prior tests intact. A passing run verifies a finite observation
  of gitlink/default-tip agreement, not scientific correctness or all
  cross-repository canonical-input bindings. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · Prepared a source-preserving refresh of all
  eight gitlinks, pins and README references to their individually observed
  default tips, with the previous pins retained in the predecessor commit and
  `PIN_REFRESH_OBSERVATION.json`. Rebound three observed canonical input blobs
  to those source cuts. Converted the historical authority-map branch pointer
  to its exact commit and labeled it historical because the file is absent at
  the observed Main default tip. This neither decides current scientific
  authority nor promotes a claim. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · B · Added strict committed-input and stable-HEAD
  checks after tests showed the older checker could combine a clean working
  manifest with a conflicting committed manifest. Local controls also found
  that a differing remote tip had been called "behind" without an ancestry
  check; the message now says "differs". Neither change weakens mathematical
  bounds or disables existing tests. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · B · Add strict current-tip verification to the
  existing pin workflow after its legacy remote check. This makes newly
  observed upstream drift fail that workflow rather than appear green;
  update pins and rerun when sources advance. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · On the reconstructed local candidate,
  executed 84 workspace tests in normal Python and 84 in optimized Python;
  both passed, including all 15 selected strict pin-checker mutations.
  Structural map and offline gitlink checks also passed. This does not claim a
  remote G7 pass, an atomic federation snapshot or mathematical certification.
  Detailed commands and source hashes: `evidence/validation_20261029.json`.
- 2026-10-29 UTC · Phase 1 · C · Workspace publication `e347db7` accidentally
  included `repos/Universal-Law-Workspace` as a ninth gitlink: the assembly
  input contained the workspace HEAD as well as the eight submodule tips.
  The publication check verified expected entries but failed to reject extra
  entries. Hosted pin and contract jobs failed on the unexpected link. Remove
  it and require an exact recursive leaf-tree comparison against the tested
  candidate before moving the ref. Retain both failed runs as evidence; do
  not weaken either check. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · Align this workspace contribution with the
  federation's active coordination in main#684 and main#685. Their integrator
  owns federation-wide consolidation and peer assignments. This repository's
  status and evidence describe its own contribution; they are not a competing
  declaration of federation closure. Reversible: yes.

- 2026-10-29 UTC · Phase 1 · C · After the unintended gitlink was removed,
  workspace contract run 40918788940 passed on `66019e4`; pin run
  40918789181 rejected Main's advance to `81acc060`. Refreshed the Main
  gitlink, pin and README reference to the observed tip. This is a new source
  cut, not proof of ongoing or atomic federation currency. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · Hosted pin run 40919435108 on `a4b0168`
  rejected a later meta-framework tip `0f5894f8`; the contract run passed.
  Refresh the meta-framework pin and README to that observed commit. The
  registry blob there is unchanged. Preserve the failed run, and require a
  fresh hosted check rather than assuming concurrent repositories are stable.
  Reversible: yes.
- 2026-10-29 UTC · Phase 1 · B · Add `tools/verify_canonical_inputs.py` and
  real-Git and mutation controls for the source-blob identity gap. Record it
  in the tool registry and run it after strict tip verification. Explicit
  historical refs remain distinguished from current gitlink inputs; no
  semantic or mathematical acceptance is inferred. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · A separate hosted formal-core run at Math-
  `8151f592` passed its Lean build, then timed out in `leanchecker` after
  900 seconds. Axiom audit, compiled inventory, executable controls and a
  success receipt were not obtained. Record the scope and retain the failure;
  the federation integrator is already investigating recheck resources in
  main#684. Reversible: yes.

- 2026-10-29 UTC · Phase 1 · C · While the canonical-input candidate was
  tested, governance- advanced from `e396002a` to `1b62ca2f`. Refresh its
  candidate gitlink, pin and README reference as another sequential source
  observation. Other agents' work remains active; the final integration must
  recheck all tips rather than infer global stability. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · B · The source check originally called every
  explicit ref differing from the gitlink "historical" without testing
  ancestry. A real-Git control with a newer explicit ref exposed the incorrect
  label. Report "separate-ref" instead; the authority map's historical context
  remains a separately documented source fact. Reversible: yes.
- 2026-10-29 UTC · Phase 1 · C · Query's downstream bundle records Math-
  `6c020d6a` rather than the observed `8151f592` gitlink. All seven recorded
  byte counts and SHA-256 values were recomputed and match, and their source
  blobs are unchanged at the newer cut. Preserve the declared snapshot rather
  than rewriting its commit identity on byte equality alone. This is scoped
  evidence, not an atomic federation or mathematical-acceptance claim.
  Reversible: yes; evidence: `evidence/query_snapshot_identity_20261029.json`.
- 2026-10-29 UTC · Phase 1 · C · Independently checked three further distinct
  query replay rows at their recorded Math commits and at the observed Math
  tip. Recorded lengths and SHA-256 values match and each Git blob is
  unchanged; the standalone RN entry has the same identity as one row. Keep
  each declared commit, without promoting scientific status. Reversible: yes;
  evidence: `evidence/query_replay_identity_20261029.json`.
- 2026-10-29 UTC · Phase 1 · B · Replaced this repository's legacy agent entry
  with the owner-directed CBZ entry and created repository-local status,
  baseline, governance, inventory and decision surfaces. They describe an
  incomplete workspace contribution, not federation closure. The previous
  agent entry and all other predecessor files remain recoverable from Workspace
  commit `45a80ab01504936b46d035c2de1f92c73ed273de`; federation-wide integration
  and shared status remain with the active main#684 coordinator. Reversible:
  yes.

## Execution checklist

1. Add end-to-end local-Git tests showing equal tips pass and each failure
   surface above is refused. Run against the old checker and retain the red
   result.
2. Implement `--require-current`, implying remote checks and failing closed on
   absent or inconsistent evidence. Keep legacy `--network` semantics.
3. Run strict tests, the full workspace suite, and mutation controls in both
   ordinary and optimized Python. Document the precise scope and limitations.
4. Reconcile the eight pin sources, three stale control blobs and historical
   authority map before any remote pin update; refresh all refs at publication.
5. Publish only verified source changes and exact observed inventory; do not
   claim final CBZ gates from synthetic source snapshots or historical results.


- 2026-10-29 19:47:31 UTC · Phase 3 · A/B · Reproduced the canonical mutation
  harness false-kill finding with a real inner checker exit 86. Exact RED
  d4ae729871d17332f9adc705cc55e082897bc5ed ran 107 hosted tests, with one
  intended failure (run 40942797333/job 123690270511). Preserve every original
  behavioral mutant and repair the evidence classifier using test-owned,
  fresh nonce-bound intended-bypass observations, result-protocol controls
  and four actual classifier source mutations. Add optimized execution to
  the existing contract workflow. Local subprocess creation was failing with
  EAGAIN; native Git data APIs and hosted execution provide a source-bound
  verification route. Reversible: yes; source history and hosted logs retain
  the RED state. Pin drift remains a separate observed failure.


- 2026-10-29 20:01:45 UTC · Phase 3 · A/C · Observed hosted contract success
  on canonical harness repair 8397f29669ba213dcc6e678dd9f8015033f1e5af:
  run 40943291131/job 123691959826 passed 110 tests in each Python mode,
  including every retained checker mutation and four classifier source
  mutations. Native Git data confirms tested PR merge
  10f9d4e8ecb98ad1e7abcced3b548160d6c6106c and source head share tree
  85d96123ab4800268ad9858a010e139cd825ad22. Preserve complete RED, GREEN
  and pin-drift job logs plus exact observation JSON. Scoped raw-log Git
  attributes preserve evidence bytes without relaxing source formatting.
  Current pins remain RED on Main and Math drift (40943291189/job123691960126).
  No mathematical or federation-baseline promotion. Reversible: yes;
  evidence: evidence/canonical-harness/OBSERVATION.json.


- 2026-10-29 20:13:06 UTC · Phase 3 · A/B · Extended the verified intended-
  outcome protocol to the adjacent strict-pin fifteen-mutant harness after
  native source audit found its outer-failure-only false-kill signature.
  Preserve all fifteen mutants and assertions. Record actual checker results
  and fresh test-owned nonce/method/outcome observations; remove observation
  coordinates from checker child environments; require exact one-test,
  one-assertion outcomes; self-test four classifier source mutations and five
  real checker crash/refusal behaviors. Preserve strict RED source
  0f0f7f4bf5cec63caaaed16894e9196c1e296e9b. Its contract run40945946596 is
  queued, not reported as executed; automatic review4417369636 corroborates
  the deterministic failure. Continue to new-source hosted qualification
  rather than idle on local EAGAIN. Reversible: yes; evidence: source history
  and PR31 exact-source records. Existing production checkers and pins unchanged.


- 2026-10-29 21:45:28 UTC · Phase 3 · B/C · Refresh the two stale Main and Math gitlinks,
  matching pins.json entries and README commit links to their independently
  observed default tips; preserve the other six pins, all checker/test bytes,
  the actual strict-harness RED and historical 115-test-per-mode success.
  Observation is sequential, not an atomic snapshot; current-head hosted tests,
  pin verification and final G7 remain pending. Reversible: yes; evidence:
  evidence/cbz-pin-observation-20261029.json.
