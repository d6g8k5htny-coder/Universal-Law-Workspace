# CBZ baseline observations

## Contract discovery adverse finding — 10 November 2026

The exact original Workspace contract workflow block at `5ee815d60d5e11cb590b2a3b274fd13104bd915d`
accepted synthetic skipped and expected-failure discoveries in both modes;
empty discovery and an ordinary failure were refused. The candidate replaces
that count-only check with the bounded result guard documented in STATUS and
GOVERNANCE. Its 14 focused local controls per mode passed, including three
guard-removal mutations. The original red logs remain in
`evidence/contract-outcome-20261110/`. A separate normal-mode synthetic
observation found that the original pin workflow also accepts skipped and
expected-failure fixtures; the pin workflow remains outside this repair. No new
current-head hosted or federation-wide gate result is claimed.

## Source-bound hosted observation — 10 November 2026, 09:11 UTC

For PR #78 head `64b4b360575b482432eb8f052d268ddcfbfca8c4` and base
`344f81f5cb1e7040dfedb2c752b9a3514775b257`, GitHub tested merge
`3ed8493993c18e5752398f5f7f655ff7898ed2f5` with tree
`a92e5876d2366ba06a085506546672be42604069`. Contract run `42787699084`,
job `129732985197`, passed 258 tests per mode without skips on CPython 3.11.
Its original artifact `13750121464`, SHA-256
`fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c`,
has 212 unique CRC-valid members. Independent verification matched all 13
declared baseline/mutant pairs per mode, their 52 source-bound events,
candidate bytes, stderr hashes and nonces. The PR and push pin jobs also
passed 258 normal-mode tests and their eight public pin checks. These results
are bound to their actual tested sources and do not qualify a later head.

The one-off artifact verifier refused missing evidence, altered source and an
inserted skip in both modes. Two source mutations of that verifier separately
reopened the matching false accepts; the synthetic adverse archives are
explicitly labeled. Original job logs, artifact bytes, verifier source,
controls and local 258-test-per-mode observations are retained in the linked
evidence bundle. None establishes final federation G0–G11 or scientific review.

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
checked. A source-bound hosted observation is recorded in the 10 November evidence; future heads require their own platform checks. The earlier
257-test local success was for the first candidate source and does not qualify
this new source. No federation-wide gate or scientific acceptance is inferred.

## Vector grader origin boundary

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

The cited local component results do not establish a final G0–G11 pass.

No CBZ-0 baseline or final baseline tag has been declared. This is an
intermediate discovery record, not a certification.

Source cut used for this stage:

- Workspace predecessor: `45a80ab01504936b46d035c2de1f92c73ed273de`.
- Main: `4ef1867175dbe1072a54a02e95f80c4e2c70a4ff`.
- Math-: `8151f592918a845bf19eb8eafaf8444540a32734`.
- The other observed submodule source identities are in `pins.json` and
  `PIN_REFRESH_OBSERVATION.json`. Default branches were observed sequentially.

| Gate | Observed state at this stage |
|---|---|
| G0–G1 Layer A auditor and full audit | Not established. The lexical Lean-source discovery is not a verified auditor. |
| G2 axiom audit | Not established for the complete federation. |
| G3 Lean build | Local formal-core execution failed because `lake` was absent; a separate hosted formal-core build at Math- `8151f592` passed. Full federation build is not established. |
| G4 kernel audit | The same hosted formal-core run timed out during `leanchecker` after 900 seconds; the complete federation audit is not established. |
| G5 full regression | Not run federation-wide. Workspace and Math- formal-core Python controls are scoped observations in STATUS.md. Workspace hosted contract run 40918511097 failed on an unexpected gitlink in `e347db7`; run 40918788940 passed on corrected commit `66019e4`. |
| G6 mutation | Strict pin-checker mutations are bounded engineering controls, not a full Layer A mutation result. |
| G7 pin sync | Candidate pins and three control blobs were rebound to a source cut. Run 40918510771 failed on an unexpected gitlink in `e347db7`; run 40918789181 rejected Main drift on `66019e4`; run 40919435108 rejected meta-framework drift on `a4b0168`. This candidate refreshes that pin and adds a source-blob check. Verify the actual candidate and all transitive cross-repo bindings separately. The authority-map source is historical. |
| G8 status truth | Partial; several inventories and source-authority boundaries remain incomplete. |
| G9 cold start | Not run. STATUS is not yet sufficient for a complete cold-start acceptance. |
| G10 Git hygiene | Not met at discovery: many branches and open PRs remain. Other agents' worktrees and stashes were not observed. |
| G11 tooling | The changed pin checker is documented in GOVERNANCE; the full federation tool/stub inventory is incomplete. |

No proof was newly declared CLOSED or QUARANTINED. Do not use this file as a
replacement for Math-'s existing proof records or as scientific acceptance.
