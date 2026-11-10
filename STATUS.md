# CBZ status — work in progress

## Python 3.11 context-exit follow-up — 10 November 2026

The first candidate at Workspace PR #78 head
`0e4162c8f0fc9c61d13ed75c3ef91407c22c236d` passed its bounded local
CPython 3.12.14 controls, but both hosted CPython 3.11.18 jobs failed: their
normal 257-test discoveries each rejected nine intended `assertRaisesRegex`
mutant failures. The contract artifact retained 13 baselines and four admitted
mutants in its summary; the other nine were refused. Optimized hosted discovery
was not reached. The original job logs, artifact and failures remain retained.

An instrumented copy of the exact candidate showed why: in Python 3.11 the
implicit context exit is attributed to the complete `with` statement span;
Python 3.12 attributed it to the assertion-call span. The follow-up source
SHA-256 is `90abecc6c203ce98614938d24b0c2f21f2a8431ff6c784680c5f6ad63c10e95d`.
It permits either observed position only for a single-item `with` whose
context is the selected test's direct `self.assertRaisesRegex` call, while
still requiring the exact selected code identity and supported oracle path.
Unknown positions and source changes fail closed. Local CPython 3.12.14 ran
five focused controls in both parent modes, including both child modes for the
context exit and four adverse origins, plus actual callsite and oracle-path
guard removals. The 13-test mutation module passed locally in normal and optimized modes; all
52 retained baseline/mutant events and their source and stderr hashes were
checked. Exact-head hosted follow-up qualification remains pending. The earlier
257-test local success was for the first candidate source and does not qualify
this new source. No federation-wide gate or scientific acceptance is inferred.

## Vector mutation-origin correction — 10 November 2026

On Workspace source `344f81f5cb1e7040dfedb2c752b9a3514775b257`, the earlier
vector mutation grader's test file SHA-256 was
`e7630a0642101e2070d73f0bcb84b22e301cfbfac5a0ed66847ee7048d23d3a4`.
Four adversarial subject-return cases, each run in normal and optimized child
mode against real fixture tests, produced `AssertionError` from deferred
runtime behavior and were incorrectly classified as selected-oracle kills.
They included mock side effects, a deferred `unittest.case` failure, a
partial bound assertion and equality evaluated during an assertion. These
are deliberately adverse cases, not proof that every historical mutation
result was false. Earlier reports and original outcomes remain preserved;
their selected-body flag alone is insufficient to establish origin against
these cases.

The first candidate had mutation-test file SHA-256
`c88d938ab224140495153305ce8e187cadb158465cdbf74d11d2c2425e08cf3d`.
It uses the live traceback, selected code identity, selected instruction source
position bound back to the compiled selected code, and an exact supported
oracle-code path. Unsupported positions, changed or missing selected source,
and unlisted paths fail closed. The finite supported oracles are the observed
`assertEqual` and `assertRaisesRegex` paths used by the 13 declared controls;
this is not a universal Python assertion-origin proof. Local CPython 3.12.14
ran the mutation-test module in both modes: 12 tests per mode with no skips,
including 13 retained source-mutant/baseline pairs per mode, the four adverse
cases and actual removals of the callsite and oracle-path guards. Each removal
reopened its matching real false kill. The retained local archive contains
original red/green logs, candidates, events and source hashes. These observations
do not replace exact-head hosted qualification or the final federation G6.

[Evidence and scope](evidence/vector-origin-20261110/README.md)

```sh
python3 -B -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
python3 -B -O -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
```

The tool verifies finite source-bound mutation outcomes for the structural
federation vector checker. The cited local controls exercise its selected
assertion-origin grading, not all mathematical claims or all repository refs.

The separately observed Workspace base pins Main `02973f3975a1c4cc91b7c51d372f65717c9b3c5c`; these ref reads are not atomic and can become stale. CBZ-0 remains unestablished.

## Main pointer after #806 — 10 November 2026

This candidate refreshes the Main gitlink and `pins.json` from `964390a94c08f00f119dc3b2e0be16180c1544e2` to separately observed default `d291b42801a26252a046d8ca78a6bd62abc448ae`. The seven other gitlinks and manifest entries remain unchanged. Eight old pin objects resolved; at the 06:09:37–06:09:39 UTC observation the seven non-Main pins matched their defaults and the old Main pin was stale. Reads were non-atomic; see [the observation](evidence/cbz-pin-observation-20261110-main806.json). Fresh strict-current, canonical-input and exact-head hosted checks are required. This does not establish final G7, scientific acceptance, successful Pages publication or CBZ-0.

## Main pointer after #805 — 10 November 2026

This candidate refreshes the Main gitlink and `pins.json` from `b6be588c82d2256c917b7d26d901085bc90319fb` to separately observed default `964390a94c08f00f119dc3b2e0be16180c1544e2`. All seven other gitlinks and pin records remain unchanged. Eight old gitlink commits resolved; at the 05:23:47–05:23:48 UTC observation the seven non-Main pins matched their default refs and the old Main pin was stale. Reads were non-atomic; see `evidence/cbz-pin-observation-20261110-main805.json`. Fresh strict-current, canonical-input and exact-head hosted results are required; this is not final G7, scientific acceptance, successful Pages publication or CBZ-0.

## Main pointer after #797 — 10 November 2026

This source cut records the Main gitlink and `pins.json` pointer at `b6be588c82d2256c917b7d26d901085bc90319fb`, replacing `31bc4c1f5b66e92bfbf327366956944ea691289c`. The other seven gitlinks and manifest entries are preserved. At the separately observed cut, all eight old gitlink commits resolved and the seven non-Main pins matched their default refs; the old Main pin was stale. Reads were non-atomic. See `evidence/cbz-pin-observation-20261110-main797.json`. Fresh `--require-current`, canonical-input and exact-head hosted results are required; no full-federation G7, successful Pages publication or CBZ-0 is claimed.


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

## Immutable-vector structural candidate — qualification pending

### Later origin correction and structural observation — 9 November 2026

The original vector mutation grader accepted an `AssertionError` from a
subject under a directory named `unittest` as a test-oracle failure. The
recorded earlier campaign remains historical; it does not qualify future
grading. The candidate grader now records the live traceback before unittest
cleanup and requires the actual selected body, dispatch and permitted unittest
code objects by identity. Its supported domain is the selected synchronous
unittest bodies and their standard unittest assertion helpers; it is not a
hostile-code sandbox or a general arbitrary-helper classifier.

At the candidate test source SHA-256
`e7630a0642101e2070d73f0bcb84b22e301cfbfac5a0ed66847ee7048d23d3a4`,
CPython 3.12.14 ran 67 focused vector tests in each mode with no skips or
failures. Each mode ran 13 clean baselines and 13 designated source mutants;
the real spoofed-path control was refused and an actual guard-removal
self-mutation exposed the false kill in both child modes. Full current-source
Workspace and hosted qualification remain to be observed.

The complete pre-pin-refresh candidate suite subsequently ran 254 Workspace
tests in each mode on CPython 3.12.14, with no failures, errors or skips. This
composition now also proposes the Main pin `b0a6c12abe87ae2a43163b3fe6ba4fa14adf389d`,
observed as the Main default after #789 merged; the preceding full-suite
results are not a hosted execution of this pin composition. Fresh pin checks
and exact-head CI remain required.

A sequential twelve-repository offline cut first failed `GIT_READ_FAILED` on
the historical Main blob `fb0e8c2275cf66dc686064f1476e99b7b3653bea`. After
the original blob was recovered and its Git identity verified, a fresh run
passed the selected structural checks: twelve repositories, eight pointers,
four canonical bindings and nine lock packages. It used Main `1902aac1`,
Math `f532c3e2` and Workspace `30a042a8`, among the selected commits. This
is not an atomic or final vector, current-tip test, remote availability,
full working-byte parity, Git hygiene, G7 or CBZ-0. The failed run remains
part of the evidence.

The later network-enabled run of the same cut failed
`NETWORK_REQUIRED_FAILURE`: 20 of 22 exact Git commit requests returned
`FETCHED_COMMIT`; the private custodian-validation and hosted-qualification
repositories returned `FETCH_FAILED` with exit 128. Their API-reconstructed
local objects do not establish authenticated native Git remote availability.

The separately documented [vector verifier](docs/cbz/FEDERATION_VECTOR.md)
checks twelve immutable source relationships, eight pointers, four canonical
byte bindings and nine native locks. It observes requested exact-commit
availability without imposing default-tip equality.

```sh
python3 -B -S tools/verify_federation_vector.py --root /absolute/siblings --vector /outside/vector.json --output /outside/new-offline.json
python3 -B -S tools/verify_federation_vector.py --root /absolute/siblings --vector /outside/vector.json --network --output /outside/new-network.json
python3 -B -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
python3 -B -O -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
```

Complete final-source normal/optimized qualification, actual live smoke and
fresh engineering review remain pending. The original sixty-two controls were declared;
they have not all passed on this final source. Local resource-exhausted
attempts receive no pass credit. Six Git-free final-source controls and static
checks completed; the three recovered code/test hashes match the preserved
native manifest. The four accompanying documentation revisions are new
proposals on the current published Workspace base, not byte-exact recovery of
the unreadable original documentation snapshot.

Full working-byte parity and Git hygiene remain unassessed. No full proof
inventory, classification/quarantine reconciliation, final G0–G11 or CBZ
criterion follows. A local unpublished candidate is not remotely available
merely because it passes offline structure. Root owns later publication,
source-bound hosted qualification, review and guarded integration.

Three reviewed counterexamples have since been added, making 65 declared
controls. The initial hosted draft intentionally retains the unchanged tool
until the canonical object-type and noncanonical path cases fail by the
expected test assertions. The tool is not admitted while those gaps remain.

Observed RED at `be512430`: 252 normal Workspace tests, six designated assertion
failures, no errors/skips; optimized not executed. The follow-up source adds
the two guards and strengthens existing descendant/filter controls, with a
thirteenth finite guard mutation. Current-source execution and fix review are
pending; this structural candidate remains unadmitted.

### Vector engineering checks observed; actual final vector outstanding

Published7ee77666c1ed848d236db8d6911ce0a784db4593 passed252normal and
252optimized Workspace tests without failures/errors/skips, including65 vector
controls and the13-mutant finite campaign. Both pin jobs also passed252normal
and their pin/canonical checks. Original printed52events bind13cleanbaselines
and13intended selected-body mutant failures per mode; ZIPmemberbytes were not
independently read. Scoped engineering fix review is complete.

The first retained-source offline attempt failed before Gitversion/repository
observations; a second launch was rejected with process-creation errno11
before execution. No actual current/final12-source vector PASS or globalG7 is
claimed. Integrating the complete self-tested structural tool leaves those
live/source obligations open, preserves both false global flags and changes
no mathematical disposition or CBZ criterion. Exact final-docheadCI must still
be observed before ordinary integration.
