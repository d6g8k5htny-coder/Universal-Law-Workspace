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

- 2026-11-04 UTC · Bounded scanner follow-up on the local composition of PR31,
  Workspace main 202f9f5c and the preserved PR32 status correction. The initial
  178-test baseline failed twice in each Python mode: a temporary archive path
  inherited an invalid enclosing .git marker, and the unmutated scanner control
  repeated that failure. Preserve those logs separately; do not call that
  composition qualified. Git context must use a real enclosing worktree, while
  a fixture needing a project boundary must create one even under repo-local
  TMPDIR. Validate candidate roots with Git, ignore ambient GIT_* redirection,
  keep searching past unvalidated markers, and reject non-enclosing results.
  OS/executable failures remain errors; nonzero Git results are unvalidated,
  not a complete diagnosis of configuration or ownership refusals. Add real
  invalid-marker, nested/linked-worktree, symlink and environment controls;
  retain existing guards and mutants. New tests on unchanged scanner source
  ran 44 tests with nine failing assertions/subtests; repaired focused tests
  passed 44 in each mode. Complete source-bound suite qualification is pending.
  No historical evidence, pins, theorem status or review disposition changes.

- 2026-11-04 19:15 UTC · Phase 3 · B/C · Align the strict-pin mutation
  contract in GOVERNANCE.md with the existing source at Workspace PR33 head
  2ad2a8a4fc5cd603690fc6e4704fdcae54a83d6d. Its two missing-ref mutants record
  an exact diagnostic demotion even when another guard still refuses; they
  do not demonstrate complete invalid-source acceptance. Retain the default
  acceptance outcome, separate remote-contact and ancestry outcomes, exact
  test/nonce/outcome binding, all fifteen mutants and all assertions. The
  pre-edit strict-pin behavior and mutation controls passed 63 tests in each
  normal and optimized Python mode. This change corrects documentation only;
  executable sources, tests, pins, historical evidence and the preserved PR32
  STATUS.md correction are unchanged. New-candidate qualification must be
  observed, not inferred from those baseline runs. Reversible: yes, ordinary
  Git history. Evidence: tests/pin_mutation_receipts.py,
  tests/test_verify_pins_mutations.py,
  docs/cbz/pin-mutation-demotion-20261029.md and the PR33 source-bound handoff.
  No inherited review-thread resolution, approval, merge or scientific status
  change is performed by this correction.

- 2026-11-05 01:48 UTC · Phase 3 · C · Refresh only the Math- pin, gitlink
  and matching README link after Math-#554 merged to
  4cc9ff6de9ed6f7887a24e459607fd1061853509. The previous pin
  dfa9b30a27ea8f8ee647bb067549fa53c7d06ef6 and its note history remain
  recoverable. All seven other pin records, canonical map, checker/test
  sources, historical evidence and PR32 STATUS.md correction are unchanged.
  At prior Workspace head 84e28cba866132ffa987e97a6eea8ba0a782b370, fresh
  full regression passed 187 tests in each normal and optimized runner mode;
  strict currentness failed exactly the Math drift, and all four canonical
  identities passed. Math's two canonical blobs also match at the new pin.
  Rationale: restore the bounded federation pin contract after upstream moved.
  New committed-source and hosted qualification must be observed separately.
  Evidence: Workspace PR33 source-bound handoff and Math- PR554 merge.
  Reversible: yes, ordinary Git history. Observations are sequential, not an
  atomic snapshot. No G7 award, CBZ-0, scientific status, inherited-thread
  disposition, approval or merge is performed by this pin refresh.

- 2026-11-05 16:28 UTC · Phase 3 · C · Refresh only the Math- pin, gitlink
  and matching README link after the completed Math-#541/#550/#548/#551/#553
  integrations advanced its default to 1a4d57ac80f2d34f39f37137ebb89569c18b8fe4.
  Preserve prior pin 4cc9ff6de9ed6f7887a24e459607fd1061853509 and its note
  history, all seven other complete pin records, canonical map, executable
  sources, tests, historical evidence and exact PR32 STATUS correction.
  Fresh baseline structure, offline pins and all four canonical identities
  passed at Workspace107b2f96; strict currentness failed exactly Math drift.
  Both configured Math canonical blobs match at the new pin. New committed
  candidate and hosted qualification remain separate obligations. Observe one
  stable source cut and stop publication if tips or ownership change, rather
  than repeatedly chasing moving defaults. Reversible through ordinary Git
  history. Evidence: Workspace PR33 handoff and Math main merge history.
  Sequential observations are not atomic, final G7, CBZ-0, scientific
  acceptance, inherited-thread disposition, approval or merge.

- 2026-11-05 17:29 UTC · Phase 3 · C · Refresh only the Math- pin, gitlink
  and matching README link after Math-#552 merged to
  f532c3e2d91a0c7679a37c733741660917a9b21b at 16:53 UTC. Fresh reads
  found only the coupled dormant Math-#547/#549 drafts remaining and no
  competing Workspace writer. Preserve prior pin 1a4d57ac and its full note
  history, all seven other complete pin records, executable sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Baseline structure, offline pins and four canonical identities passed at
  Workspace 6b8f7722; strict currentness failed exactly the new Math drift.
  Both Math canonical blobs are unchanged. New candidate and hosted checks
  remain separate obligations. Retain the prior completed qualification
  unchanged and publish only one guarded cut if tips and custody still match.
  Reversible through ordinary Git history. Sequential tip observations are
  not atomic, final G7, CBZ-0, scientific acceptance, inherited-thread
  disposition, approval or merge. Evidence: Workspace PR33 and Math PR552.

- 2026-11-05 21:25 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#730 merged to
  bc416552f9f4f19cf6a56aafd6cdd38ac8922701 at 21:07 UTC. Fresh custody
  and queue reads found no competing Workspace writer or imminent integration.
  Preserve prior Main pin d2b0216e and its full note history, all seven other
  complete pin records, executable sources, tests, workflows, canonical map,
  historical evidence and exact PR32 STATUS blob. Baseline structure, offline
  pins and four canonical identities passed at Workspace e0ab644d; strict
  currentness failed exactly the new Main drift. The authority-map input
  remains explicitly historical at a01c72f1, not current Main authority.
  New candidate and hosted qualification remain separate obligations. Retain
  the prior evidence archive unchanged; publish only one guarded source cut
  if defaults and custody still match. Main's existing federation-drift
  failure and other reviews are not resolved by refreshing this pin.
  Reversible through ordinary Git history. No final G7, CBZ-0, scientific
  acceptance, inherited-thread disposition, approval or merge is claimed.


- 2026-11-05 22:31 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#751 merged the reviewed exact-location
  federation-drift repair to 17952bb921899dec55f45fce389ca2cfb8438e6f. Preserve prior Main pin bc416552f9f4f19cf6a56aafd6cdd38ac8922701
  and its full note history, all seven other complete pin records, executable
  sources, tests, workflows, canonical map, historical evidence and exact PR32
  STATUS blob. The integrated Main source passed fresh verify, landing,
  federation-drift and adverse self-test, formal, architecture, navigation,
  browser, public-shop and public-intake checks; that engineering qualification
  changes no mathematical status. New Workspace committed-source and hosted
  qualification remain separate obligations. Sequential tip observations are
  not atomic, and this refresh is not final G7, CBZ-0, scientific acceptance,
  inherited-thread disposition, approval or merge. Reversible through ordinary
  Git history; evidence: Main#751 and Workspace PR33.

- 2026-11-05 22:55 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#754 closed the reviewed declaration-kind
  exemption gap and merged normally to
  165e99b9f2f0f6b8885dec2f73295bfd1c5604cb. Preserve prior Main pin 17952bb921899dec55f45fce389ca2cfb8438e6f
  and its full note history, all seven other complete pin records, executable
  sources, tests, workflows, canonical map, historical evidence and exact PR32
  STATUS blob. The exact Main head passed the drift crawler's 88 behavior and
  mutation tests in normal and optimized modes, live federation crawl, formal,
  architecture, navigation and public-shop jobs. This custody-only refresh
  changes no theorem, bound, kernel result or scientific status. New Workspace
  committed-source and hosted qualification remain separate obligations.
  Sequential tip observations are not atomic, and this is not final G7, CBZ-0,
  scientific acceptance or a full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#754 and the Workspace pin-refresh PR.

- 2026-11-06 00:22 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#720 repaired and qualified the G11
  auditor component and merged normally to
  62611e73d3e4bab4e6ac30b9a6f96af310c7d3f3. Preserve prior Main pin 165e99b9f2f0f6b8885dec2f73295bfd1c5604cb
  and its full note history, all seven other complete pin records, executable
  sources, tests, workflows, canonical map, historical evidence and exact PR32
  STATUS blob. The exact Main head passed 38 G11 controls and all 75 adverse
  mutations in normal and optimized modes, plus live federation crawl, formal,
  architecture, navigation, browser, public-shop and public-intake checks.
  The earlier digest RED, target-mismatch RED and their review history remain
  preserved. This custody-only refresh changes no theorem, bound, kernel result
  or scientific status. New Workspace committed-source and hosted qualification
  remain separate obligations. Sequential tip observations are not atomic, and
  this is not final G7, CBZ-0, scientific acceptance or full Layer A clearance.
  Reversible through ordinary Git history; evidence: Main#720 and the Workspace
  pin-refresh PR.

- 2026-11-06 04:53 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#752's G12 census and declaration-scope
  A8 repair merged normally to
  a7295bf20741c111da06d72faa846536ff76fa1c. Preserve prior Main pin
  62611e73d3e4bab4e6ac30b9a6f96af310c7d3f3 and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  The exact refreshed PR head passed 86 focused statement-fuzz tests in normal,
  optimized and warning-as-error modes; all 3,782 census semantic records were
  unchanged after the namespace repair; and its five fresh current-base hosted
  workflows completed successfully across all ten jobs before protected merge.
  The preserved CPython-3.12 full-discovery mutation-harness failure is not
  relabelled or hidden. This custody-only refresh changes no theorem, bound,
  kernel result or scientific status. New Workspace committed-source and hosted
  qualification remain separate obligations. Sequential tip observations are
  not atomic, and this is not final G7, CBZ-0, scientific acceptance or full
  Layer A clearance. Reversible through ordinary Git history; evidence:
  Main#752 and the Workspace pin-refresh PR.

- 2026-11-06 05:47 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#721's provenance-safe federation
  reference crawler merged normally to
  6096be098e66401b2aa63c8727d9a1e01c058c2d. Preserve prior Main pin
  a7295bf20741c111da06d72faa846536ff76fa1c and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  The exact refreshed PR head passed 61 focused controls in normal and
  optimized modes, all 3 grader-source mutants in both modes, all 109
  provenance-safe source mutants, a strict current-pin crawl of 29,832
  references with zero blocking, and five fresh hosted workflows across all
  ten jobs. Historical host termination, RED shards and the narrower 108/108
  evidence remain preserved. This custody-only refresh changes no theorem,
  bound, kernel result or scientific status. New Workspace committed-source
  and hosted qualification remain separate obligations. Sequential tip
  observations are not atomic, and this is not final G7, CBZ-0, scientific
  acceptance or full Layer A clearance. Reversible through ordinary Git
  history; evidence: Main#721 and the Workspace pin-refresh PR.

- 2026-11-06 06:29 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#756 amended the bounded G12 statement
  fuzz registration and merged normally to
  4e8f58760ecc20fb3bf2f989eaf4b9ecfe3caa75. Preserve prior Main pin
  6096be098e66401b2aa63c8727d9a1e01c058c2d and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#756 changed only `DECISIONS.md`, `GOVERNANCE.md` and `STATUS.md`;
  it changed no theorem, bound, certifying implementation or test. Its exact
  refreshed head passed the local workspace-landing and navigation checks and
  five fresh current-base hosted workflows across all ten jobs. Earlier G12
  receipts, limitations and failure boundaries remain preserved. This
  custody-only refresh changes no mathematical or scientific status. New
  Workspace committed-source and hosted qualification remain separate
  obligations. Sequential tip observations are not atomic, and this is not
  final G7, CBZ-0, scientific acceptance or full Layer A clearance.
  Reversible through ordinary Git history; evidence: Main#756 and the
  Workspace pin-refresh PR.

- 2026-11-06 08:08 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#697 and Main#758 merged normally to
  4cd4799112dcf274ca13e4f208c685544944b6de and
  c933b81f59929af85a7f2de5123df1ccfadd7f80. Preserve prior Main pin
  4e8f58760ecc20fb3bf2f989eaf4b9ecfe3caa75 and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#697 integrated the bounded global-auditor repair; Main#758 repaired the
  CPython-3.12 empty-discovery adverse control so it isolates the nonempty
  guard. Every hosted head workflow for both integrations completed
  successfully. Two fresh local Main full-suite attempts remain preserved as
  RED because unrelated 20-second child processes timed out; each exact
  timed-out case passed when rerun alone, and the repaired node-regression file
  passed all 60 tests in both normal and optimized modes. This custody-only
  refresh changes no theorem, bound, kernel result or scientific status. New
  Workspace committed-source and hosted qualification remain separate
  obligations. Sequential tip observations are not atomic, and this is not
  final G7, CBZ-0, scientific acceptance or full Layer A clearance.
  Reversible through ordinary Git history; evidence: Main#697, Main#758 and
  the Workspace pin-refresh PR.

- 2026-11-06 10:12 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#760 merged normally as
  04989724b5142f8eea8d41946d0367d0372d845a. Preserve prior Main pin
  c933b81f59929af85a7f2de5123df1ccfadd7f80 and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#760 integrates the qualified #698 reconstruction, released P1–P3
  repairs and the bounded ordinary-string hole traversal repair; its native
  tree is ce8a2b1687460e7dddfa0aca09b8ef01afa99d39 and its two parents preserve
  current Main and the reviewed candidate head. All required and candidate-
  head checks completed successfully before protected merge. The exact
  documented residual remains: total work is the sum of hole lengths, so many
  unmatched openings and deeply nested matched holes retain quadratic worst
  cases. This custody-only refresh changes no theorem, bound, kernel result or
  scientific status. New Workspace committed-source and hosted qualification
  remain separate obligations. Sequential tip observations are not atomic,
  and this is not final G7, CBZ-0, scientific acceptance or full Layer A
  clearance. Reversible through ordinary Git history; evidence: Main#760 and
  the Workspace pin-refresh PR.

- 2026-11-06 12:55:58 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#761, Main#762 and Main#763 merged
  normally to 299c7fad72f1079b87b2d044b2d30f2098678f29. Preserve prior
  Main pin 04989724b5142f8eea8d41946d0367d0372d845a and its full note
  history, all seven other complete pin records, executable Workspace
  sources, tests, workflows, canonical map, historical evidence and exact
  PR32 STATUS blob. Main#761 added the truthful canonical CBZ surfaces;
  Main#762 repaired G11 workflow-step scope with 39/39 unit tests and 76/76
  exact mutations in both modes; Main#763 registered the active G11 tooling
  residue and reduced the observed undocumented/unreferenced count from 55
  to 48 without manufacturing green. Every hosted head workflow for all
  three integrations completed successfully. The exact remaining G11
  boundary is 20 active tools whose exercise attribution is missed and 28
  tools with no current exercise detected. This custody-only refresh changes
  no theorem, bound, kernel result or scientific status. New Workspace
  committed-source and hosted qualification remain separate obligations.
  Sequential tip observations are not atomic, and this is not final G7,
  CBZ-0, scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#761, Main#762, Main#763 and the
  Workspace pin-refresh PR.

- 2026-11-08 19:53:37 UTC · Phase 3 · C · Refresh only the Main pin, gitlink
  and matching README link after Main#764, Main#766, Main#767 and Main#768
  merged normally to 2540673afc7533584d9f82194fba9c786b8c037b.
  Preserve prior Main pin 299c7fad72f1079b87b2d044b2d30f2098678f29
  and its full note history, all seven other complete pin records, executable
  Workspace sources, tests, workflows, canonical map, historical evidence and
  exact PR32 STATUS blob. Main#764 repaired bounded G11 active-tool
  attribution; Main#766 repaired aggregate-alias provenance; Main#767 closed
  three architecture CLI exercise-attribution gaps; and Main#768 closed the
  Atlas formal-source-bridge exercise gap. All six post-#768 workflows
  completed successfully at the exact merge commit. The decoded G11 job ran
  265 controls per workflow mode and killed all 328 designated mutations per
  required mode with a 263-test baseline and zero skips. The separate
  navigation artifact records 2,423 discovered tests with 37 preserved skips.
  The exact current G11 census still exits nonzero with zero production
  findings and 28 retained browser-check tools. This custody-only refresh
  changes no theorem, bound, kernel result or scientific status. New Workspace
  committed-source and hosted qualification remain separate obligations.
  Sequential tip observations are not atomic, and this is not final G7,
  CBZ-0, scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#764, Main#766, Main#767, Main#768,
  durable checkpoint v126 and the Workspace pin-refresh PR.

- 2026-11-08 21:03:53 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#769 merged normally to
  90ae56160ebf0ab1f81e3de33efc07bafcbfcc09. Preserve prior Main pin 2540673afc7533584d9f82194fba9c786b8c037b and
  its full note history, all seven other complete pin records, executable
  Workspace sources, tests, workflows, canonical map, historical evidence and
  exact PR32 STATUS blob. Main#769 integrated the focused website-navigation
  browser regression and fail-closed Chrome-channel launch controls. Before
  merge, its exact head passed all required checks; the real hosted browser
  run executed 24/24 cases with zero failures and zero page errors. The exact
  G11 census still exits nonzero with zero production findings and 27 retained
  browser-check tools. Post-merge Main workflows and new Workspace
  committed-source qualification remain separate observations. This
  custody-only refresh changes no theorem, bound, kernel result or scientific
  status. Sequential tip observations are not atomic, and this is not final
  G7, CBZ-0, scientific acceptance or full Layer A clearance. Reversible
  through ordinary Git history; evidence: Main#769, durable checkpoint v127
  and this Workspace pin-refresh PR.

- 2026-11-08 22:33:34 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#770 merged normally to
  6bf348787f19a6c9159d13c393a5a1ee93b09ecb. Preserve prior Main pin
  90ae56160ebf0ab1f81e3de33efc07bafcbfcc09 and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#770 integrated the focused Atlas accessibility browser regression,
  an explicit installed-Chrome channel default, retained sandboxing, and
  fail-closed runner, mutation and workflow-reference controls. Its exact
  focused controls passed 38/38 in normal and optimized modes; the complete
  Main suite passed 2,433 tests with 25 preserved skips in each mode. The
  protected merge followed all required checks. Independently downloaded
  pull-request and published artifacts each record four light/dark 320/390
  pixel browser cases with 12/12 checks, zero failures, Chrome
  156.0.8078.79, `channel=chrome` and sandboxing enabled. The exact G11
  census still exits nonzero; its unresolved count fell from 27 to 26 without
  manufacturing green. This custody-only refresh changes no theorem, bound,
  kernel result or scientific status. Sequential tip observations are not
  atomic, and this is not final G7, CBZ-0, scientific acceptance or full
  Layer A clearance. Reversible through ordinary Git history; evidence:
  Main#770, durable checkpoint v129 and this Workspace pin-refresh PR.

- 2026-11-09 00:54:02 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#771 merged normally to
  1046e3aceb869617efa349f94e48638bb5ceb030. Preserve prior Main pin
  6bf348787f19a6c9159d13c393a5a1ee93b09ecb and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#771 integrated the existing Atlas accessible-list browser check into
  the hosted public-shop job, retained Chromium sandboxing, added an installed
  Chrome-channel default plus explicit executable override, and added
  fail-closed runner, mutation and workflow-reference controls. Its exact
  head passed all five hosted workflows, including a real Chrome 156 run with
  7/7 light and 7/7 dark cases, and fresh isolated native controls passed
  7/7 in normal and optimized modes. One package-style local unittest command
  produced three import errors because tests is not a package; the native
  script entrypoints corrected that command-shape error without changing
  source. The exact G11 census remains nonzero with 25 retained unresolved
  tools; no green baseline is manufactured. This custody-only refresh changes
  no theorem, bound, kernel result or scientific status. Sequential tip
  observations are not atomic, and this is not final G7, CBZ-0, scientific
  acceptance or full Layer A clearance. Reversible through ordinary Git
  history; evidence: Main#771, durable checkpoint v133 and this Workspace
  pin-refresh PR.

- 2026-11-09 02:08:51 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#772 merged normally to
  6deca3198c4b11b2d1208df904f5b942cd3e4bfb. Preserve prior Main pin
  1046e3aceb869617efa349f94e48638bb5ceb030 and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#772 recovered the exact current Atlas source bridge for manifest blob
  8d43188691c695f66e233727322484da22662a58, added fail-closed runner,
  mutation and workflow-reference controls, and refreshed only the five
  deterministic public-site asset pins affected by that bridge. Its exact
  head passed all eight pull-request workflow runs plus both readiness-triggered
  required public-intake checks. Focused custody tests passed 67/67 in normal
  and optimized modes; source-bridge tests passed 20/20 and all three adverse
  mutations were killed per mode. Local full Main discovery preserved two
  Chromium launch errors because this managed executor forbids the singleton
  socket; hosted Chrome qualification passed. The exact G11 census remains
  nonzero with 24 retained unresolved tools; no green baseline is
  manufactured. This custody-only refresh changes no theorem, bound, kernel
  result or scientific status. Sequential tip observations are not atomic,
  and this is not final G7, CBZ-0, scientific acceptance or full Layer A
  clearance. Reversible through ordinary Git history; evidence: Main#772,
  durable checkpoint v133 and this Workspace pin-refresh PR.

- 2026-11-09 02:59:53 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#773 merged normally to
  e18798544f16479436283d71689ae635a1817b20. Preserve prior Main pin
  6deca3198c4b11b2d1208df904f5b942cd3e4bfb and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#773 was documentation-only: it refreshed STATUS, PROOF_INDEX,
  GOVERNANCE, TOOLING and BASELINE from the stale 7 November snapshot and
  appended DECISIONS without changing a proof, theorem statement, axiom,
  mathematical bound, kernel outcome, authorship record or historical
  failure. Its exact head passed all five pull-request workflow runs, and the
  automated review completed with no findings. The canonical correction
  candidate's first pre-commit Workspace suites ran 187 tests per mode and
  failed exactly the committed-real-tree control because that control binds
  `HEAD` while the new gitlink was only staged; no test was removed or
  weakened, and fresh exact-commit qualification remains required.
  The canonical correction
  truthfully retains the 24-tool G11 failure, the managed Chromium regression
  failure, every unawarded CBZ criterion and the absence of a same-pass
  G0--G11 result. This custody-only refresh changes no scientific status.
  Sequential tip observations are not atomic, and this is not final G7,
  CBZ-0, scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#773, durable checkpoint v134 and this
  Workspace pin-refresh PR.

- 2026-11-09 03:57:36 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#774 merged normally to
  7712277ced9170c8d61d8f324319f40177c145b1. Preserve prior Main pin
  e18798544f16479436283d71689ae635a1817b20 and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#774 retired one unsupported historical Atlas browser acceptance driver
  from the current operational tool surface instead of manufacturing A8 or
  G11 credit. Its exact 20,118-byte source remains recoverable at native Git
  blob 9576fd34806528484a3898665c19cabe9eb3797c and in Main ancestry; the
  two qualified consumers retain only their small byte-identity helpers.
  The exact head passed all 12 hosted checks, including required verify,
  public-intake and public-shop, the fresh formal Lean/kernel lane, both G11
  jobs, browser/navigation, architecture and federation drift. Automated
  review completed with no findings. The merge commit is GitHub-signed, has
  parents e18798544f16479436283d71689ae635a1817b20 and
  52c24401d1c0b58c9f1940ead30fe5d1518259de, and preserves qualified tree
  1bafc1d181ddc161c51d58bfe3084a118d2d9bbf. The bounded G11 residue is
  reduced from 24 to 23 tools and remains FAIL. No theorem, bound, axiom,
  proof disposition, kernel outcome, authorship, historical failure or
  scientific status changed. The pre-commit Workspace suites ran 187 tests
  per mode and failed exactly the committed-real-tree control because that
  control binds `HEAD` while the new gitlink was staged; no test was removed
  or weakened. This Workspace candidate still requires its own committed-tree
  qualification. Sequential
  tip observations are not atomic, and this is not final G7, CBZ-0,
  scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#774, durable checkpoint v135 and this
  Workspace pin-refresh PR.

- 2026-11-09 05:18:28 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#775 merged normally to
  31150f4a0736cb79bf33e366b6b725b061126000. Preserve prior Main pin
  7712277ced9170c8d61d8f324319f40177c145b1 and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#775 retired two undocumented and unreferenced historical Atlas browser
  drivers while preserving their exact native blobs and the unchanged frozen
  F973 source record. Its final candidate retained zero production G11
  findings and reduced the bounded residue from 23 to 21 tools; G11 remains
  FAIL. The exact head passed all 12 hosted checks, including required verify,
  public-intake and public-shop, the fresh formal Lean/kernel lane, both G11
  jobs, browser/navigation, architecture and federation drift. Automated
  review completed with no findings. The merge commit is GitHub-signed, has
  parents 7712277ced9170c8d61d8f324319f40177c145b1 and
  c7f1c736b944635d0ca95e34a8357c2aabf7dac0, and preserves qualified tree
  b3f103e72a12cc766519c28bae92265162f2955e. Complete local Main discovery
  remains RED with the same two managed Chromium singleton-socket errors and
  23 skips in each mode; no regression-100% result is manufactured. Durable
  v136 remains bound to its independently read-back status and evidence
  identities. No theorem, bound, axiom, proof disposition, kernel outcome,
  authorship, historical failure or scientific status changed. This Workspace
  candidate still requires its own committed-tree qualification. Sequential
  tip observations are not atomic, and this is not final G7, CBZ-0,
  scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#775, durable checkpoint v136 and this
  Workspace pin-refresh PR.

- 2026-11-09 06:28:19 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#776 merged normally to
  848cd66bbf4a73e77a6f3e1fff64ce4796150f6d. Preserve prior Main pin
  31150f4a0736cb79bf33e366b6b725b061126000 and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#776 recoverably retired eight documented historical Atlas browser
  drivers that had no current executable reference or exercise. All plans,
  reports, failures, authorship and scientific status remain unchanged; exact
  native recovery identities are registered in Main STATUS. Its final
  candidate retained zero production G11 findings, reduced the registry from
  90 to 82 tools and the bounded unresolved residue from 21 to 13 tools, and
  still exited 1; G11 remains FAIL. Its 263/263 auditor controls and 328/328
  designated mutants passed per mode. Both corrected complete discoveries ran
  2,459 tests and preserved exactly two managed Chromium singleton-socket
  errors and 23 skips; no regression-100% result is manufactured. The exact
  head passed all ten hosted jobs across five workflows. The merge commit is
  GitHub-signed, has parents 31150f4a0736cb79bf33e366b6b725b061126000
  and 5b4116bce98c5a3c25ff5117af6399711863a295, and preserves qualified tree
  2f48833cbd051545be1a7d383137c99e5fa57a12. Durable v137 remains bound to
  its independently read-back status and evidence identities. No theorem,
  bound, axiom, proof disposition, kernel outcome, authorship, historical
  failure or scientific status changed. This Workspace candidate still
  requires its own committed-tree qualification. Sequential tip observations
  are not atomic, and this is not final G7, CBZ-0, scientific acceptance or
  full Layer A clearance. Reversible through ordinary Git history; evidence:
  Main#776, durable checkpoint v137 and this Workspace pin-refresh PR.

- 2026-11-09 07:45:24 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#777 merged normally to
  ed5d83b7eff354cd7025117f4d2371422acd816b. Preserve prior Main pin
  848cd66bbf4a73e77a6f3e1fff64ce4796150f6d and its full note history,
  all seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#777 recoverably retired the final thirteen documented historical
  research/browser drivers that had no current executable reference or
  exercise. All plans, reports, preserved failures, authorship and scientific
  status remain unchanged; exact native recovery identities are registered in
  Main STATUS. Its final candidate passed the bounded G11 census with 69 tools,
  zero unresolved tools and zero production findings. Its 263/263 auditor
  controls and 328/328 designated mutants passed per mode. Both complete
  discoveries ran 2,459 tests with exit 0 and 25 explicit skips; no
  full-regression-100% result is manufactured. The exact head passed all eight
  jobs across five workflows. The merge commit is GitHub-signed, has parents
  848cd66bbf4a73e77a6f3e1fff64ce4796150f6d and
  c9a2c1e04496f5d2b2fe585eeb5ae8f8d40b5fa2, and preserves qualified tree
  87fdabafadfdb1ee2b766222b6d0c313de8d9a89. Six landed workflows were
  observed. Five passed on their first attempts. The workspace-landing formal
  job's source controls passed, then its pinned Elan archive download returned
  HTTP 504; that actual failure and its 175-byte evidence artifact remain
  preserved. A targeted retry at the identical landed commit succeeded on
  attempt 2, including formal/kernel evidence, architecture, landing checks
  and verify. Durable v138 remains bound to its independently read-back status
  and evidence identities. No theorem, bound, axiom, proof disposition,
  authorship, historical failure or scientific status changed. This Workspace
  candidate still requires its own committed-tree qualification. Sequential
  tip observations are not atomic, and this is not final G7, CBZ-0,
  scientific acceptance or full Layer A clearance. Reversible through
  ordinary Git history; evidence: Main#777, durable checkpoint v138 and this
  Workspace pin-refresh PR.

- 2026-11-09 08:38:40 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#778 merged normally to
  5ebe5771d44160f56d4f2fd1e11726858d17dc90. Preserve prior Main pin
  ed5d83b7eff354cd7025117f4d2371422acd816b and its full note history, all
  seven other complete pin records, executable Workspace sources, tests,
  workflows, canonical map, historical evidence and exact PR32 STATUS blob.
  Main#778 was documentation-only: it bound all five canonical Main surfaces
  and the append-only decision ledger to the signed Main#777 / Workspace#51
  serial boundary and independently read-back durable v139. It did not alter
  a theorem, proof source, quarantine, bound, axiom, G11 implementation,
  authorship, historical failure, kernel outcome or scientific status. The
  G11 component remains explicitly author-observed; 25 regression skips remain
  and no full-regression-100%, final G7, full Layer A, cold-start, same-pass
  G0--G11, CBZ-0 or terminal Partial result is manufactured. Its exact head
  passed all jobs across five workflows and received a scoped read-only
  engineering review with no change request and explicit re-execution limits.
  The GitHub-signed merge has parents
  ed5d83b7eff354cd7025117f4d2371422acd816b and
  84b935a3370d52d785bfa1dd0f8ab9abac2b5a76 and preserves qualified tree
  ccb76aaa970d5f95b1f7e0c9adf88604cd7f202a. This Workspace candidate still
  requires its own committed-tree qualification. Sequential tip observations
  are not atomic. Reversible through ordinary Git history; evidence: Main#778,
  durable checkpoint v139 and this Workspace pin-refresh PR.

- 2026-11-09 18:02:13 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main#779 merged normally to
  6ab126beda65e19865b8468b52f8757ac2324e1f. Preserve the prior Main pin
  5ebe5771d44160f56d4f2fd1e11726858d17dc90 and its full note history, all
  seven other complete pin records, Workspace sources, tests, workflows,
  canonical map, historical evidence and STATUS. The Main change requires
  full history for its navigation workflow and a separate no-skip execution
  of the two existing history-backed reader classes. Hosted navigation ran
  2,469 tests with 25 skips and the separate reader suite ran 20 with no skips;
  the prior 37-skip log remains preserved. Five other applicable sandbox,
  two browser and two Lean controls ran separately without skips at the same
  tested tree, while ten pytest-policy controls and the #525 composition test
  were separately exercised locally. These do not constitute one complete
  no-skip regression. The protected merge was initially rejected because the
  required trusted public-intake workflow failed to start during GitHub's
  scheduled protection brownout; the failed runs are retained. After that
  window, run 42670053409 succeeded and normal required-check integration
  produced a GitHub-verified signed merge with parents 5ebe5771… and
  2d440383… and tree df5509f1f25dc406bad95ab4b88c288300901a98. A separate
  adverse test found a subject-origin false kill in the existing node-status
  freshness mutation grader; its repair remains in progress and no mutation
  evidence from that grader is promoted. This pin candidate still requires
  its own committed-tree and hosted qualification. Sequential tip observations
  are not atomic; no final G7, full regression, complete Layer A audit,
  scientific acceptance, CBZ-0 or terminal Partial is claimed. This custody
  change is reversible through Git history; evidence: Main#779, checkpoint
  v144 and the associated independently retained observations.

- 2026-11-09 18:13 UTC — Preserve the initial hosted qualification failures
  for Workspace #53 at head `39dadaba87c92ce886037904711abf25791e293b`.
  Federation-contract run 42671456239 and pins run 42671456244 each stopped
  before creating any job; GitHub's run pages reported internal server
  errors, with correlation IDs `45f9d099-4d5b-48e2-b25c-de9a5083d55e`
  and `5da24b9c-5c24-4295-9321-42ad1108d721`, respectively. GitHub
  refused each targeted failed-job retry with HTTP 403, stating that the
  workflow run cannot be retried. These are platform outcomes, not passing
  tests or source-failure diagnoses. Preserve them and qualify this updated
  candidate through the ordinary pull-request checks on its actual head.

- 2026-11-09 18:22 UTC — On the next candidate head
  `bd617949f349805b87f51ede2b793553f30c542f`, federation-contract run
  42672115232 and pins run 42672114965 likewise failed before creating
  jobs. GitHub's run pages reported internal server errors with correlation
  IDs `9e77ee74-79dc-4d23-a8f9-276fa00576cd` and
  `60025573-4dd6-46c3-9589-a0a33d31778f`. Preserve those separate
  outcomes. Later Main pull-request workflows were observed starting jobs;
  this is a reason to attempt fresh ordinary Workspace checks, not a passing
  Workspace qualification or permission to bypass protected integration.

- 2026-11-09 18:49 UTC · Phase 3 · C · Refresh only the Main pin,
  gitlink and matching README link after Main #782 merged through the normal
  expected-head endpoint as f1ef3a2babecca0f0d4eb35b018dc81d30e9d62c.
  Preserve previous Main pin 6ab126beda65e19865b8468b52f8757ac2324e1f and
  its complete note history, all seven other pin records, Workspace sources,
  tests, workflows, canonical map, historical evidence and STATUS. Main #782
  corrects the node-status freshness mutation grader's subject-origin false
  kill, adds adverse checks and preserves the original eleven mutations and
  old results. It also marks one observed engineering source record stale
  without changing its historical pin. Current-head hosted grader and G11
  jobs passed; the required workspace-landing aggregate passed on synthetic
  merge d5b5c8f3987e3dbfafff23f0e2b75ac53969c738. Navigation reported 2,489
  tests with 25 skips plus 20 separate no-skip history tests. Earlier-tree
  full local regression ran 2,489 tests with 25 skips in each mode; those skips
  remain unmet, and no final G0–G11 or complete Layer A audit is claimed.
  Published merge tree 5b771047cb384a9bb167ed2df505489cee1cbf7d has parents
  6ab126be… and 9bf048e9aeee3b846da92fba6e4d0708dee310e7. No theorem, bound,
  axiom, proof disposition, authorship, historical failure or scientific
  status changed. The new Workspace candidate requires its own exact-tree
  checks. Sequential tip observations are not atomic; this does not claim
  final G7, cold start, scientific acceptance, CBZ-0 or terminal Partial.
  The prior Workspace post-merge federation startup failure remains recorded.
  A local initial worktree command mistakenly used the Main commit as a
  Workspace base; the remote reported “not our ref” and the attempt was
  interrupted, creating no worktree or branch. The correct base is Workspace
  2441baf051312878ca28e462d455cfbcd8e91b20. This custody change is reversible
  through Git history; evidence: Main #782 and board #738 comment 6748477101.

- 2026-11-09 UTC · Phase 2 · B · Refresh the Workspace Main gitlink and
  manifest pin from `f1ef3a2babecca0f0d4eb35b018dc81d30e9d62c` to the
  separately observed default `b1d36c80403acc96d257b9e71140a6cb83a595af`
  after Main #780. Preserve all seven other pins, canonical inputs, earlier
  outcomes, documentation and the prior source history. Main #780 restored a
  bounded tracked-source inventory and isolated Git status metadata; its
  mutation classifiers remain subject to independently reproduced
  subject-origin false kills, and its author reported a separate Node run with
  one failure among 767 cases. Neither is relabeled as a pass. Main #783 is
  concurrently active and a later Main move requires another guarded pin
  refresh. This sequential observation does not establish an atomic final G7,
  complete regression, Layer A audit, proof closure, scientific acceptance,
  CBZ-0 or terminal Partial. Candidate-specific checks remain to be observed.
  Reversible through Git history.

- 2026-11-09 UTC · Phase 2 · B · Refresh the Workspace Main gitlink and
  manifest pin from `b1d36c80403acc96d257b9e71140a6cb83a595af` to
  `7738e4c2e0881dd952772421877d9854364d272f` after Main #783. Individually
  observed defaults for all eight pinned repositories matched the proposed
  pins during 20:06:32--20:06:38 UTC; this was not an atomic observation.
  Preserve all other pins, prior notes, outcomes, source history and canonical
  inputs. Main #783 updates baseline documents and decisions; it does not
  qualify the known inventory classifier defect, resolve the preserved Node
  failure or close any mathematical claim. The separate inventory-origin and
  Node repair candidates remain under test. Candidate-specific checks and a
  fresh comparison before normal integration remain required. No final G7,
  regression, Layer A audit, scientific acceptance, CBZ-0 or terminal Partial
  follows from this pin. Reversible through Git history.

- 2026-11-09 UTC · Phase 2 · B · Refresh the Workspace Main gitlink and
  manifest pin from `7738e4c2e0881dd952772421877d9854364d272f` to
  `c81b7572f3c690338db9d66fdea582fc68f4a73f` after Main #785. Individually
  observed defaults for all eight pinned repositories matched these proposed
  pins during 20:39:18--20:39:23 UTC; this was not an atomic observation.
  Preserve all other pins, prior notes, outcomes, source history and canonical
  inputs. Main #785 repairs the bounded inventory mutation-origin controller;
  its hosted normal regression ran 2,576 tests with 25 skips, and the separate
  local optimized full run has no final result. The historical false kills and
  Node failure remain retained. Candidate-specific checks and a fresh head
  comparison before normal integration remain required. No final G7, full
  no-skip regression, Layer A audit, scientific acceptance, CBZ-0 or terminal
  Partial follows from this pin. Reversible through Git history.

- 2026-11-09 UTC · Phase 2 · B · Refresh the Workspace Main gitlink and
  manifest pin from `c81b7572f3c690338db9d66fdea582fc68f4a73f` to
  `1902aac113761974c4569f78acb6a8baadabb7f1` after Main #784, which also
  carries #781's original authored entry-routing commits. Eight separately
  observed defaults matched these proposed pins during 20:56:56--20:57:00
  UTC; this was not atomic. Preserve all other pins, earlier notes, source
  history, outcomes and canonical inputs. The tested #784 merge ran 767 Node
  tests per Python preparation mode with no failures or skips; its normal Main
  regression ran 2,576 tests with 25 skips. The previous failed Node execution
  remains retained. These observations do not establish final G7, a no-skip
  full regression, Layer A clearance, scientific acceptance, CBZ-0 or
  terminal Partial. Candidate checks and a fresh head comparison are required
  before normal integration. Reversible through Git history.

## 2026-11-09 — structural vector verifier staged for qualification

- Phase 2, Layer B/tooling. OpenAI Codex implemented the bounded verifier in
  isolated local history based on Workspace
  `1c552538e6a8952548e2bd5297a0031dda1f94e7`. Four local library slices end at
  `9d4ed4933e0a581279209a32d23990db3651beac`; the complete final source was
  preserved with a seven-file manifest and private snapshot. Frozen source
  checkouts and peer pin updates were preserved.
- The tool/test files were recovered in memory from exact creation/patch inputs
  after local process creation became unavailable. Recovery matched the native
  final Git blobs and SHA-256 identities:
  tool `b917bcf9ef11d0845b7db948e485d81e56018d34`;
  behavioral tests `680c11361139c921cbd6441c2aba908a82550212`;
  mutation tests `978872fc7c1a736dd43cfeb79415c4f0d2da7671`.
  The tool also matched every available intermediate development digest.
- The four accompanying documentation files are consciously new proposed
  revisions on published Workspace
  `8a7aac8626438967830ea5a516a944ce48759018`. Existing current governance,
  status and decisions bytes remain intact prefixes. These new revisions are
  not claimed byte-identical to the unreadable original four documentation
  files. No pin, gitlink, module or README pin-row change belongs to this tool.
- Initial source/index, pointer/canonical and lock slices passed respectively
  13, 21 and 33 focused controls in normal/optimized modes. Eight network
  controls passed normally and the then-complete 41 controls passed optimized.
  A twelve-mutant normal campaign passed on an earlier CLI source. Those
  observations remain source-bound and do not qualify the later final source.
- Root's target-TOML-name counterexample was observed red then fixed through
  the minimal sibling TOML check. Selected-input executable-mode and cleanup
  refinements retain their red/green records. SDGA's existing stale general
  lock name is preserved; general configuration semantics remain unassessed.
- Final focused local attempts hit process-creation exhaustion: each ran only
  39 tests because setup also failed; normal retained three failures/sixteen
  errors and optimized three failures/ten errors. They receive no pass credit.
  One later Git-free control launch could not start at all. A single successful
  fork-free check then parsed the three final Python files, checked all twelve
  unique mutation anchors/mutated syntax, and passed six Git-free controls.
  The full 62-control final population, hosted normal/optimized execution,
  actual live smoke and fresh engineering review remain pending.
- Root authorized only seven unreferenced public source/document blobs for
  review and later draft qualification. The implementer created no commit,
  ref, PR or settings through that staging, and uploaded no source snapshot,
  log, private vector/report or private repository contents. The private local
  evidence and original snapshot remain preserved separately. Root owns the
  explicit qualification commit, later publication and guarded integration.
- Structural scope only: selected sources/index/inputs, eight pointers, four
  canonical byte bindings, nine native locks and explicit optional remote
  availability. Full working parity and Git hygiene stay unassessed; CBZ and
  semantic-completeness flags stay false. An unpublished/equal-tree local
  commit cannot substitute for observing an actual published commit remotely.
  No Layer A, global G7, final G0–G11, CBZ criterion, scientific independence
  or CBZ-0 is awarded. Ordinary Git additions remain reversible.

## 2026-11-09 — reviewed counterexamples staged before vector fixes

Root preserved the complete Workspace `8a4d2248e9646ba3181a61defc90d13a01fe08ac`
source prefix and Main pin `1902aac113761974c4569f78acb6a8baadabb7f1`.
The original tool and mutation-control blobs remain unchanged. A behavioral
test revision adds rejection cases for tree and annotated-tag canonical refs,
and dependency paths whose lexical normalization hides impossible detours.
Static engineering review identified these acceptance gaps; actual hosted
assertion failures must precede the corresponding production fixes. There are
65 declared controls after these additions. No static finding or failure in
setup is counted as a successful rejection experiment. Complete normal and
optimized qualification, the twelve-mutant campaign, live source smoke and
fresh fix review remain pending. No admission, proof classification, G7 or
CBZ-0 result follows from publishing this draft.

## 2026-11-09 — actual vector RED and minimal guarded candidate

- Root independently read contract run `42699263867`, attempt1, job
  `129439316391`, at initial head `be512430997757f415c5463ccfa9ad3056a504c5`.
  Normal ran252 with exactly6 test-body `ValueError not raised` assertion
  failures, zero errors/skips; optimized was not executed after normal failed.
  Both ordinary pin jobs independently observed the same six failures.
- Author adds only native canonical commit-kind refusal and a normalized-dir
  guard before existing target resolution/membership. The path policy forbids
  hidden detours, permits safe leading-parent traversal through captured real
  ancestors, and does not require a literal shortest relative path.
- Existing timeout and filter tests now exercise an actual inherited-pipe
  descendant with owned cleanup and attributed-file native Git positive
  probes. Their new source has no passing credit until executed.
- Original twelve mutation tuples are unchanged; a thirteenth removes the
  new canonical-kind guard and must be detected by its designated body.
  The complete ordinary suite includes65 vector controls plus187 existing
  controls. Full normal/optimized current-source tests, live smoke and fresh
  fix review remain pending. No mathematical, G7 or CBZ status changes.

## 2026-11-09 — timeout fixture race and retained hosted experiments

- Scoped static review confirmed both production fixes and identified a test
  fixture race: a waiting parent could reap the killed descendant before its
  own group-kill exit. This was not reproduced or counted as a RED failure.
  Keep the descendant referenced while the parent sleeps; the adopting test
  remains responsible for its owned waitpid cleanup. Assertions are unchanged.
- Ordinary contract CI retains normal and optimized mutation experiments in
  separate runner-temporary directories through the existing evidence env.
  An always-running bounded reporter prints original summary/event fields,
  hashes and missing/read-failure observations without regrading them. An
  immutable pinned upload action retains original logs, candidate copies and
  child event/transcript files, including after failures. Contents permission
  remains read-only; required test commands/exit handling are unchanged.
  The previous source/run outcomes retain their identities. Fresh actual
  execution and scoped review must qualify this new composition.
