# CBZ baseline observations

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

This source contains a candidate correction whose mutation-test file SHA-256 is
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
