# CBZ status — work in progress

This repository maps the Universal Law federation and its pinned sources.
Clean Baseline Zero is not established. The current discovery is recorded in
`INVENTORY.md` and `INVENTORY.json`; it is incomplete and is not a full proof,
branch-custody, workflow or local-worktree inventory.

Federation coordination and integration are tracked in
[`main#684`](https://github.com/d6g8k5htny-coder/main/issues/684) and
[`main#685`](https://github.com/d6g8k5htny-coder/main/pull/685). This file
records this workspace contribution and does not replace their shared record.

## Verified so far

- A reconstructed snapshot of the pre-change workspace was checked locally:
  its structural map and offline pin checks passed, as did 66 Python tests.
- At the inspected Math- source, the formal-core source identity check and
  244 Python tests passed in each of normal and optimized modes. This is not a
  Lean build, kernel recheck, complete axiom audit or proof acceptance.
- A separate hosted run at Math- `8151f592` completed the formal-core Lean
  build, then failed when its kernel recheck timed out after 900 seconds. The
  subsequent axiom audit, compiled inventory, executable controls and success
  receipt were not produced. This does not establish the formal gate.
- The strict current-tip pin checker candidate passed the complete workspace
  suite of 84 tests in each of normal and optimized Python on the reconstructed
  local candidate. The suite detected all 15 named pin-checker mutations in
  both modes. This is scoped engineering evidence, not a full Layer A audit.
  Current hosted/federation-wide gates must be run against the actual committed
  state before they can be reported green.
- Hosted runs 40918510771 and 40918511097 on Workspace commit `e347db7`
  failed: the published Git tree accidentally contained an extra gitlink
  `repos/Universal-Law-Workspace` absent from the tested local candidate.
  The correction removed that gitlink. The corrected contract run passed;
  its pin run rejected Main drift after Main advanced. See
  `evidence/hosted_validation_20261029.json` for exact run identities.
- The Main gitlink was subsequently refreshed to `81acc060` after that drift.
  On that newer commit `a4b0168`, the contract run passed, while the strict
  pin run rejected a newer meta-framework tip. This candidate refreshes that
  pin and adds canonical-input identity checks; its hosted result must be
  observed on the actual candidate commit.
- Query's seven-row downstream bundle remains pinned to Math- `6c020d6a`;
  the seven recorded files match their declared sizes and SHA-256 hashes and
  have the same Git blob identities at Math- `8151f592`. The commits are
  different, so this observation does not change the historical snapshot or
  prove all transitive pins current. See
  `evidence/query_snapshot_identity_20261029.json`.
- Three other query replay rows also match their recorded byte identities and
  the observed Math blobs; the standalone RN row duplicates one of them.
  Their separate historical commits remain unchanged. See
  `evidence/query_replay_identity_20261029.json`.

## Remaining

The 12 CBZ criteria remain unmet or not yet verified as a single final pass.
Open work includes the complete obligation and branch inventory, verified
Layer A auditor and full-tree audit, full Lean/kernel/axiom checks, complete
regression/mutation runs, all cross-repository control-source consistency,
precise proof quarantine, and cold-start qualification. Current peer work and
existing history have not been disposed of by this status file.

## How to verify this repository

```sh
python3 tools/check_workspace.py
python3 tools/verify_pins.py
python3 tools/verify_pins.py --network
python3 tools/verify_pins.py --require-current
python3 tools/verify_canonical_inputs.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -O -m unittest discover -s tests -p 'test_*.py' -v
```

Strict pin verification needs network access to the listed public Git remotes.
It tests observed tips sequentially, not an atomic cross-repository snapshot.
The exact scope of these tools and their self-checks is in `GOVERNANCE.md`;
decisions are in `DECISIONS.md`. The canonical mathematical proof inventory
currently remains in `Math-/PROOF_INDEX.md`; no closed/quarantine conversion
has been asserted here. No quarantines were created by this initial stage.

Layer A: no sorry/admit closures, unverified axiom injection, floating-point
certification, weakened mathematical bounds or silently disabled failing
tests; disclose vacuity; report actual verification and auditor limitations.


## Canonical-checker evidence repair

The original canonical-input mutation harness could count a silent checker
crash as a killed mutation. A real hosted adverse control at
`d4ae729871d17332f9adc705cc55e082897bc5ed` demonstrated that defect:
107 tests ran, with exactly that adverse control failing (run 40942797333,
job 123690270511). The repair retains all 13 checker mutants and adds
control-owned, per-run intended-bypass observations plus four classifier
source mutations. Both normal and optimized modes are now in the contract
workflow. At exact source head `8397f29669ba213dcc6e678dd9f8015033f1e5af`, hosted run
40943291131/job 123691959826 passed all 110 tests in both modes, including all
13 canonical source mutants, four classifier source mutants and the retained
15 strict pin mutants. The tested PR merge and head have identical Git trees.
See `evidence/canonical-harness/OBSERVATION.json` and the retained raw logs.
Strict pins failed separately at that head because Main and Math had advanced;
this component success is not current G7 or CBZ-0.


## Strict-pin harness qualification

Follow-on review found the same false-kill class in the older strict-pin
mutation harness. Its fifteen source mutants and all assertions are retained.
A real silent-checker adverse control is preserved at
`0f0f7f4bf5cec63caaaed16894e9196c1e296e9b`. The corresponding hosted run
40945946596/job 123701194251 subsequently ran 111 tests and failed exactly
the silent-checker adverse control. Automatic review 4417369636 also
corroborated that the adverse control fails for the intended reason.

At source head `0ec778db868d2aef9cb172402a67c7ffd6c4d1de`, hosted
run 40949547576/job 123713717737 passed 115 tests in each normal and optimized
mode, including the retained strict-pin mutations and classifier controls.
That is a source-cut component observation, not qualification of the newer
pin candidate. Pin jobs at the prior head failed `--require-current` for
Main and Math; no final cross-repository gate is established.

## Non-atomic candidate pin refresh

At 2026-10-29 21:45:28 UTC, eight public default branches were observed sequentially. The Main
and Math gitlinks, pins.json entries and README table were refreshed to
`1e2be44c69e08e47472041ac329e1b27f7dec793` and `9f8dbb4d18b9f3ebd9ffac6b0caa42df9f343966`, respectively; the other six already matched
their observed tips. These observations are not an atomic federation snapshot.
At the 2026-10-29 21:45:28 UTC observation, this candidate's hosted verification was still pending. The later exact-head results and subsequent default-tip drift are recorded below. Neither the historical pass nor this status update establishes current G7 or CBZ-0.

[Exact observation](evidence/cbz-pin-observation-20261029.json).


## Exact-head hosted qualification and subsequent pin drift (2026-10-30)

The candidate at Workspace PR #31 head `9d4ec7bdc79295f4e67944be352d8643d3cc7bff` was subsequently tested through synthetic merge `0c485d84122440c066e0ff195eba493313e82ea2`; the merge and PR head have the identical tree `31f4d8e7f987981f683e963f976470aac479d93e`.

- Contract run [40960506324](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/actions/runs/40960506324), job `123751708721`, completed successfully on that exact head. Its contract suite ran 115 tests in normal Python and 115 in optimized Python, both passing.
- Pin run [40960506599](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/actions/runs/40960506599), job `123751710163`, completed successfully on that exact head. Its log shows `verify_pins.py --network`, `verify_pins.py --require-current`, and `verify_canonical_inputs.py` all succeeded; four canonical inputs were checked, followed by the 115-test suite in the workflow's configured mode. The strict-current result is valid for that run's remote-tip observation only.

At the fresh default-branch readback used for this correction, Main `main` was `11e28815163e15223e8827fe6ff47a1faaf36ebd`, while this candidate pins Main `1e2be44c69e08e47472041ac329e1b27f7dec793`; Math- `main` was `19a55750451b8016b50d1d20be6a18c021807ecb`, while this candidate pins Math- `9f8dbb4d18b9f3ebd9ffac6b0caa42df9f343966`. Both observed default tips differ from the recorded pins. Therefore the successful `--require-current` run is historical to its exact source cut and does not establish current G7. This correction did not remeasure the other six repositories or establish an atomic federation snapshot; no pin, README, gitlink or workflow was changed. No G7 or CBZ-0 completion is claimed.
